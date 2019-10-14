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
from Platforms.Discord.commandindex import command_register

async def apiDiscordCommandsCreate(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/commands/create
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get stuff
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	trigger:str = Data.getStr("trigger", "")
	complex_:bool = Data.getBool("complex", False)
	function:str = Data.getStr("function", "")
	content:str = Data.getStr("content", "")
	hidden:str = Data.getBool("hidden", False)
	cooldown:int = Data.getInt("cooldown", cls.Web.BASE.Limit.DISCORD_COMMANDS_COOLDOWN)
	require:int = Data.getInt("require", 0)
	required_currency:int = Data.getInt("required_currency", 0)

	# guild id check
	if not guild_id:
		return await missingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	# trigger
	if not trigger:
		return await missingData(cls, WebRequest, msg="missing 'trigger'")
	# only take the first argument trigger, since everything else can't be typed in a channel
	trigger = trigger.split(" ")[0]

	#cooldown
	if not (cls.Web.BASE.Limit.DISCORD_COMMANDS_COOLDOWN <= cooldown <= 600 ):
		return await apiWrongData(cls, WebRequest, msg="'cooldown' is wrong")

	#currency
	if not required_currency >= 0 :
		return await apiWrongData(cls, WebRequest, msg="'required_currency' is wrong")

	# if not complex
	# check if the function actully exists
	if complex_:
		if not function:
			return await missingData(cls, WebRequest, msg="missing 'function'")
		if not function in [cmd["function"].__name__ for cmd in command_register]:
			return await apiWrongData(cls, WebRequest, msg=f"'{function}' is not a valid value for field 'function'")

	# check if already exists
	res:list = await getDiscordServerCommands(cls.Web.BASE.Discord, guild_id, trigger = trigger)
	if res:
		return await apiDiscordCommandExists(cls, WebRequest, command=trigger)

	# get/check discord
	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	# check limit
	commands:list = await getDiscordServerCommands(cls.Web.BASE.Discord, guild_id)
	if len(commands) >= cls.Web.BASE.Limit.DISCORD_COMMANDS_AMOUNT:
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

	cls.Web.BASE.PhaazeDB.query("""
		INSERT INTO discord_command
		(
		 `guild_id`, `trigger`, `content`,
		 `function`, `complex`, `hidden`,
		 `require`, `required_currency`, `cooldown`
		)
		VALUES (
		 %s, %s, %s,
		 %s, %s, %s,
		 %s, %s, %s)""",
		(guild_id, trigger, content,
		function, complex_, hidden,
		require, required_currency, cooldown)
	)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Created new command: S:{guild_id} T:{trigger}", require="discord:commands")

	return cls.response(
		text=json.dumps( dict(msg="new command successfull created", command=trigger, status=200) ),
		content_type="application/json",
		status=200
	)
