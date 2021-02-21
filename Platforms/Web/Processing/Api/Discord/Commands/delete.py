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
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.discordcommand import DiscordCommand
from Platforms.Web.utils import authDiscordWebUser
from Platforms.Discord.db import getDiscordServerCommands, getDiscordSeverSettings
from Platforms.Discord.logging import loggingOnCommandDelete

async def apiDiscordCommandsDelete(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/commands/delete
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required vars
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	command_id:str = Data.getStr("command_id", "", must_be_digit=True)

	# checks
	if not guild_id:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not command_id:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'command_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await cls.Tree.Api.Discord.errors.apiDiscordGuildUnknown(cls, WebRequest)

	# get command
	res_commands:list = await getDiscordServerCommands(PhaazeDiscord, guild_id=guild_id, command_id=command_id)

	if not res_commands:
		return await cls.Tree.Api.Discord.Commands.errors.apiDiscordCommandNotExists(cls, WebRequest, command_id=command_id)

	CommandToDelete:DiscordCommand = res_commands.pop(0)

	# get user info
	AuthDiscord:AuthDiscordWebUser = await authDiscordWebUser(cls, WebRequest)
	if not AuthDiscord.found:
		return await cls.Tree.Api.errors.apiMissingAuthorisation(cls, WebRequest)

	# get member
	CheckMember:discord.Member = Guild.get_member(int(AuthDiscord.User.user_id))
	if not CheckMember:
		return await cls.Tree.Api.Discord.errors.apiDiscordMemberNotFound(cls, WebRequest, guild_id=guild_id, user_id=AuthDiscord.User.user_id)

	# check permissions
	if not (CheckMember.guild_permissions.administrator or CheckMember.guild_permissions.manage_guild):
		return await cls.Tree.Api.Discord.errors.apiDiscordMissingPermission(cls, WebRequest, guild_id=guild_id, user_id=AuthDiscord.User.user_id)

	cls.BASE.PhaazeDB.query("""
		DELETE FROM `discord_command` WHERE `guild_id` = %s	AND `id` = %s""",
		(CommandToDelete.server_id, CommandToDelete.command_id)
	)

	# logging
	GuildSettings:DiscordServerSettings = await getDiscordSeverSettings(PhaazeDiscord, guild_id, prevent_new=True)
	log_coro:Coroutine = loggingOnCommandDelete(PhaazeDiscord, GuildSettings, Deleter=CheckMember, command_trigger=CommandToDelete.trigger)
	asyncio.ensure_future(log_coro, loop=cls.BASE.DiscordLoop)

	cls.BASE.Logger.debug(f"(API/Discord) Commands: {guild_id=} deleted {command_id=}", require="discord:commands")
	return cls.response(
		text=json.dumps(dict(msg="Commands: Deleted entry", deleted=CommandToDelete.trigger, status=200)),
		content_type="application/json",
		status=200
	)
