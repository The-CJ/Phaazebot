from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.discordwebuserinfo import DiscordWebUserInfo
from Platforms.Discord.commandindex import command_register
from Platforms.Web.Processing.Api.errors import (
	apiMissingData,
	apiWrongData,
	apiMissingAuthorisation
)
from Platforms.Web.Processing.Api.Discord.errors import (
	apiDiscordGuildUnknown,
	apiDiscordMemberNotFound,
	apiDiscordMissingPermission
)
from .errors import (
	apiDiscordCommandExists,
	apiDiscordCommandLimit
)

async def apiDiscordCommandsCreate(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/commands/create
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	trigger:str = Data.getStr("trigger", "").lower().split(" ")[0]
	complex_:bool = Data.getBool("complex", False)
	function:str = Data.getStr("function", "")
	content:str = Data.getStr("content", "")
	hidden:str = Data.getBool("hidden", False)
	cooldown:int = Data.getInt("cooldown", cls.Web.BASE.Limit.DISCORD_COMMANDS_COOLDOWN_MIN)
	require:int = Data.getInt("require", 0, min_x=0)
	required_currency:int = Data.getInt("required_currency", 0, min_x=0)

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not trigger:
		return await apiMissingData(cls, WebRequest, msg="missing 'trigger'")

	if not (cls.Web.BASE.Limit.DISCORD_COMMANDS_COOLDOWN_MIN <= cooldown <= cls.Web.BASE.Limit.DISCORD_COMMANDS_COOLDOWN_MAX ):
		return await apiWrongData(cls, WebRequest, msg="'cooldown' is wrong")

	# if not complex
	# check if the function actully exists
	if not complex_:
		if not function:
			return await apiMissingData(cls, WebRequest, msg="missing 'function'")
		if not function in [cmd["function"].__name__ for cmd in command_register]:
			return await apiWrongData(cls, WebRequest, msg=f"'{function}' is not a valid value for field 'function'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	# check if already exists and limits
	res:list = cls.Web.BASE.PhaazeDB.selectQuery("""
		SELECT
			COUNT(*) AS `all`,
			SUM(
				CASE WHEN LOWER(`discord_command`.`trigger`) = LOWER(%s)
				THEN 1 ELSE 0 END
			) AS `match`
		FROM `discord_command`
		WHERE `discord_command`.`guild_id` = %s""",
		( trigger, guild_id )
	)

	if res[0]["match"]:
		return await apiDiscordCommandExists(cls, WebRequest, command=trigger)

	if res[0]["all"] >= cls.Web.BASE.Limit.DISCORD_COMMANDS_AMOUNT:
		return await apiDiscordCommandLimit(cls, WebRequest)

	# get user info
	DiscordUser:DiscordWebUserInfo = await cls.getDiscordUserInfo(WebRequest)
	if not DiscordUser.found:
		return await apiMissingAuthorisation(cls, WebRequest)

	# get member
	CheckMember:discord.Member = Guild.get_member(int(DiscordUser.user_id))
	if not CheckMember:
		return await apiDiscordMemberNotFound(cls, WebRequest, guild_id=guild_id, user_id=DiscordUser.user_id)

	# check permissions
	if not (CheckMember.guild_permissions.administrator or CheckMember.guild_permissions.manage_guild):
		return await apiDiscordMissingPermission(cls, WebRequest, guild_id=guild_id, user_id=DiscordUser.user_id)

	# create new
	new:dict = dict(
		guild_id = guild_id,
		trigger = trigger,
		content = content,
		function = function,
		complex = complex_,
		hidden = hidden,
		require = require,
		required_currency = required_currency,
		cooldown = cooldown
	)

	cls.Web.BASE.PhaazeDB.insertQuery(table="discord_command", content=new)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Created new command: S:{guild_id} T:{trigger} N:{str(new)}", require="discord:commands")

	return cls.response(
		text=json.dumps( dict(msg="new command successfull created", command=trigger, status=200) ),
		content_type="application/json",
		status=200
	)
