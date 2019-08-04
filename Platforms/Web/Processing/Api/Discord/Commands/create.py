from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Web.Processing.Api.errors import missingData, apiWrongData, apiMissingAuthorisation
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown, apiDiscordMemberNotFound, apiDiscordMissingPermission, apiDiscordCommandLimit, apiDiscordCommandExists
from Platforms.Discord.utils import getDiscordServerCommands
from Utils.Classes.discorduserinfo import DiscordUserInfo
from Utils.dbutils import validateDBInput

async def apiDiscordCommandsCreate(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/commands/create
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	guild_id:str = Data.get("guild_id")
	if not guild_id:
		return await missingData(cls, WebRequest, msg="missing 'guild_id'")

	if not guild_id.isdigit():
		return await apiWrongData(cls, WebRequest, msg="'guild_id' must be a number")

	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	# check limit
	commands:list = await getDiscordServerCommands(cls.Web.BASE.Discord, guild_id)
	if len(commands) >= cls.Web.BASE.Limit.DISCORD_COMAMNDS_AMOUNT:
		return await apiDiscordCommandLimit(cls, WebRequest)

	# get user info
	DiscordUser:DiscordUserInfo = await cls.getDiscordUserInfo(WebRequest)
	if not DiscordUser.found:
		return await apiMissingAuthorisation(cls, WebRequest)

	# get member
	CheckMember:discord.Member = Guild.get_member(int(DiscordUser.user_id))
	if not CheckMember:
		return await apiDiscordMemberNotFound(cls, WebRequest, guild_id=guild_id, user_id=DiscordUser.user_id)

	# check permissions
	if not (CheckMember.guild_permissions.administrator or CheckMember.guild_permissions.manage_guild):
		return await apiDiscordMissingPermission(cls, WebRequest, guild_id=guild_id, user_id=DiscordUser.user_id)

	trigger:str = Data.get("trigger")
	if not trigger:
		return await missingData(cls, WebRequest, msg="missing 'trigger'")

	# only take the first argument, since everything else cant be typed in a cannel
	trigger = validateDBInput(str, trigger.split(" ")[0])

	res:list = cls.Web.BASE.PhaazeDB.query("""SELECT COUNT(*) as c FROM discord_command WHERE `guild_id` = %s AND `trigger` = %s""", (guild_id, trigger))
	if res[0]["c"]:
		return await apiDiscordCommandExists(cls, WebRequest, command=trigger)

	content:str = validateDBInput(str, Data.get("content"))
	function:str = validateDBInput(str, Data.get("function"))
	complex_:bool = validateDBInput(bool, Data.get("complex"))
	hidden:bool = validateDBInput(bool, Data.get("hidden"))
	require:str = validateDBInput(int, Data.get("require"), 0)
	required_currency:str = validateDBInput(int, Data.get("required_currency"), 0)

	cls.Web.BASE.PhaazeDB.query("""
		INSERT INTO discord_command
		(`guild_id`, `trigger`, `content`,
		 `function`, `complex`, `hidden`,
		 `require`, `required_currency`
		)
		VALUES (
		 %s, %s, %s,
		 %s, %s, %s,
		 %s, %s)""",
		(guild_id, trigger, content,
		function, complex_, hidden,
		require, required_currency)
	)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Created new command: S:{guild_id} T:{trigger}", require="discord:commands")

	return cls.response(
		text=json.dumps( dict(msg="new command successfull created", command=trigger, status=200) ),
		content_type="application/json",
		status=200
	)
