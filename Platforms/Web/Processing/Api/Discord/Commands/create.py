from typing import TYPE_CHECKING, Coroutine
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import asyncio
import discord
from aiohttp.web import Response
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.authdiscordwebuser import AuthDiscordWebUser
from Utils.Classes.storagetransformer import StorageTransformer
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.extendedrequest import ExtendedRequest
from Platforms.Discord.logging import loggingOnCommandCreate
from Platforms.Discord.commandindex import command_register
from Platforms.Discord.db import getDiscordSeverSettings
from Platforms.Web.utils import authDiscordWebUser

async def apiDiscordCommandsCreate(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/commands/create
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	Create:StorageTransformer = StorageTransformer()
	Create["guild_id"] = Data.getStr("guild_id", "", must_be_digit=True)
	Create["trigger"] = Data.getStr("trigger", "").lower().split(" ")[0]
	Create["active"] = Data.getBool("active", True)
	Create["complex"] = Data.getBool("complex", False)
	Create["function"] = Data.getStr("function", "", len_max=256)
	Create["content"] = Data.getStr("content", "", len_max=1750)
	Create["hidden"] = Data.getBool("hidden", False)
	Create["cooldown"] = Data.getInt("cooldown", cls.BASE.Limit.discord_commands_cooldown_min)
	Create["require"] = Data.getInt("require", 0, min_x=0)
	Create["required_currency"] = Data.getInt("required_currency", 0, min_x=0)

	# checks
	if not Create["guild_id"]:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not Create["trigger"]:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing 'trigger'")

	if not (cls.BASE.Limit.discord_commands_cooldown_min <= Create["cooldown"] <= cls.BASE.Limit.discord_commands_cooldown_max):
		return await cls.Tree.Api.errors.apiWrongData(cls, WebRequest, msg="'cooldown' is wrong")

	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(Create["guild_id"]))
	if not Guild:
		return await cls.Tree.Api.Discord.errors.apiDiscordGuildUnknown(cls, WebRequest)

	# if not complex
	# check if the function actually exists
	if not Create["complex"]:
		if not Create["function"]:
			return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing 'function'")
		if Create["function"] not in [cmd["function"].__name__ for cmd in command_register]:
			return await cls.Tree.Api.errors.apiWrongData(cls, WebRequest, msg=f"'{Create['function']}' is not a valid value for field 'function'")

	# check if already exists and limits
	res:list = cls.BASE.PhaazeDB.selectQuery("""
		SELECT
			COUNT(*) AS `all`,
			SUM(
				CASE WHEN LOWER(`discord_command`.`trigger`) = LOWER(%s)
				THEN 1 ELSE 0 END
			) AS `match`
		FROM `discord_command`
		WHERE `discord_command`.`guild_id` = %s""",
		(Create["trigger"], Create["guild_id"])
	)

	if res[0]["match"]:
		return await cls.Tree.Api.Discord.Commands.errors.apiDiscordCommandExists(cls, WebRequest, trigger=Create["trigger"])

	if res[0]["all"] >= cls.BASE.Limit.discord_commands_amount:
		return await cls.Tree.Api.Discord.Commands.errors.apiDiscordCommandLimit(cls, WebRequest, limit=cls.BASE.Limit.discord_commands_amount)

	# get user info
	AuthDiscord:AuthDiscordWebUser = await authDiscordWebUser(cls, WebRequest)
	if not AuthDiscord.found:
		return await cls.Tree.Api.errors.apiMissingAuthorisation(cls, WebRequest)

	# get member
	CheckMember:discord.Member = Guild.get_member(int(AuthDiscord.User.user_id))
	if not CheckMember:
		return await cls.Tree.Api.Discord.errors.apiDiscordMemberNotFound(cls, WebRequest, guild_id=Create["guild_id"], user_id=AuthDiscord.User.user_id)

	# check permissions
	if not (CheckMember.guild_permissions.administrator or CheckMember.guild_permissions.manage_guild):
		return await cls.Tree.Api.Discord.errors.apiDiscordMissingPermission(cls, WebRequest, guild_id=Create["guild_id"], user_id=AuthDiscord.User.user_id)

	cls.BASE.PhaazeDB.insertQuery(
		table="discord_command",
		content=Create.getAllTransform()
	)

	# logging prep
	log_dict:dict = Create.getAllTransform()

	# logging
	GuildSettings:DiscordServerSettings = await getDiscordSeverSettings(PhaazeDiscord, Create["guild_id"], prevent_new=True)
	log_coro:Coroutine = loggingOnCommandCreate(PhaazeDiscord, GuildSettings, Creator=CheckMember, command_trigger=Create["trigger"], command_info=log_dict)
	asyncio.ensure_future(log_coro, loop=cls.BASE.DiscordLoop)

	cls.BASE.Logger.debug(f"(API/Discord) Commands: {Create['guild_id']=} added: {Create['trigger']=}", require="discord:commands")
	return cls.response(
		text=json.dumps(dict(msg="Commands: Added new entry", entry=Create["trigger"], status=200)),
		content_type="application/json",
		status=200
	)
