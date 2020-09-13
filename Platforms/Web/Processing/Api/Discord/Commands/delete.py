from typing import TYPE_CHECKING, Coroutine
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import asyncio
import discord
from aiohttp.web import Response, Request
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.discordwebuserinfo import DiscordWebUserInfo
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Web.Processing.Api.errors import apiMissingData
from Platforms.Discord.db import getDiscordServerCommands, getDiscordSeverSettings
from Platforms.Discord.logging import loggingOnCommandDelete
from Utils.Classes.discordcommand import DiscordCommand
from Platforms.Web.Processing.Api.errors import apiMissingAuthorisation
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown, apiDiscordMemberNotFound, apiDiscordMissingPermission
from .errors import apiDiscordCommandNotExists

async def apiDiscordCommandsDelete(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
	Default url: /api/discord/commands/delete
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required vars
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	command_id:str = Data.getStr("command_id", "", must_be_digit=True)
	trigger:str = Data.getStr("trigger", "")

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if (not command_id) and (not trigger):
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'command_id' or 'trigger'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	# get command
	res_commands:list = await getDiscordServerCommands(cls.Web.BASE.Discord, guild_id, command_id=command_id, trigger=trigger)

	if not res_commands:
		return await apiDiscordCommandNotExists(cls, WebRequest, trigger=trigger, command_id=command_id)

	CommandToDelete:DiscordCommand = res_commands.pop(0)

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

	cls.Web.BASE.PhaazeDB.query("""
		DELETE FROM `discord_command` WHERE `guild_id` = %s	AND `id` = %s""",
		(CommandToDelete.server_id, CommandToDelete.command_id)
	)

	# logging
	GuildSettings:DiscordServerSettings = await getDiscordSeverSettings(PhaazeDiscord, guild_id, prevent_new=True)
	log_coro:Coroutine = loggingOnCommandDelete(PhaazeDiscord, GuildSettings, Deleter=CheckMember, command_trigger=CommandToDelete.trigger)
	asyncio.ensure_future(log_coro, loop=cls.Web.BASE.DiscordLoop)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Commands: {guild_id=} deleted [{command_id=}, {trigger=}]", require="discord:commands")
	return cls.response(
		text=json.dumps( dict(msg="Commands: Deleted entry", deleted=CommandToDelete.trigger, status=200) ),
		content_type="application/json",
		status=200
	)
