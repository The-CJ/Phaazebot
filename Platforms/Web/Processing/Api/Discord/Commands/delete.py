from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Web.Processing.Api.errors import apiMissingData
from Platforms.Discord.utils import getDiscordServerCommands
from Utils.Classes.discordwebuserinfo import DiscordWebUserInfo
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

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not command_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'command_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	# get command
	res_commands:list = await getDiscordServerCommands(cls.Web.BASE.Discord, guild_id, command_id=command_id)

	if not res_commands:
		return await apiDiscordCommandNotExists(cls, WebRequest)

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
		DELETE FROM `discord_command`
		WHERE `discord_command`.`guild_id` = %s
			AND `discord_command`.`id` = %s
			AND `discord_command`.`trigger` = %s""",
		(CommandToDelete.server_id, CommandToDelete.command_id, CommandToDelete.trigger)
	)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Deleted command: S:{guild_id} I:{command_id}", require="discord:commands")

	return cls.response(
		text=json.dumps( dict(msg="command successfull deleted", status=200) ),
		content_type="application/json",
		status=200
	)
