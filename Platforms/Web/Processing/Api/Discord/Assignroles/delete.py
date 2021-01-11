from typing import TYPE_CHECKING, Coroutine
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import asyncio
import discord
from aiohttp.web import Response, Request
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.discordwebuser import DiscordWebUser
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.discordassignrole import DiscordAssignRole
from Platforms.Discord.db import getDiscordServerAssignRoles, getDiscordSeverSettings
from Platforms.Discord.logging import loggingOnAssignroleDelete
from Platforms.Web.Processing.Api.errors import apiMissingAuthorisation, apiMissingData
from Platforms.Web.Processing.Api.Discord.errors import (
	apiDiscordGuildUnknown,
	apiDiscordMemberNotFound,
	apiDiscordMissingPermission
)
from .errors import apiDiscordAssignRoleNotExists

async def apiDiscordAssignrolesDelete(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
	Default url: /api/discord/assignroles/delete
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required vars
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	assignrole_id:str = Data.getStr("assignrole_id", "", must_be_digit=True)
	role_id:str = Data.getStr("role_id", "", must_be_digit=True)

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if (not assignrole_id) and (not role_id):
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'assignrole_id' or 'role_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	# get user info
	DiscordUser:DiscordWebUser = await cls.getDiscordUserInfo(WebRequest)
	if not DiscordUser.found:
		return await apiMissingAuthorisation(cls, WebRequest)

	# get member
	CheckMember:discord.Member = Guild.get_member(int(DiscordUser.user_id))
	if not CheckMember:
		return await apiDiscordMemberNotFound(cls, WebRequest, guild_id=guild_id, user_id=DiscordUser.user_id)

	# check permissions
	if not (CheckMember.guild_permissions.administrator or CheckMember.guild_permissions.manage_guild):
		return await apiDiscordMissingPermission(cls, WebRequest, guild_id=guild_id, user_id=DiscordUser.user_id)

	# get assign roles
	res_assignroles:list = await getDiscordServerAssignRoles(cls.Web.BASE.Discord, guild_id, assignrole_id=assignrole_id, role_id=role_id)

	if not res_assignroles:
		return await apiDiscordAssignRoleNotExists(cls, WebRequest, role_id=role_id, assignrole_id=assignrole_id)

	AssignRoleToDelete:DiscordAssignRole = res_assignroles.pop(0)

	cls.Web.BASE.PhaazeDB.deleteQuery("""
		DELETE FROM `discord_assignrole` WHERE `guild_id` = %s AND `id` = %s""",
		(AssignRoleToDelete.guild_id, AssignRoleToDelete.assignrole_id)
	)

	# logging
	GuildSettings:DiscordServerSettings = await getDiscordSeverSettings(PhaazeDiscord, guild_id, prevent_new=True)
	log_coro:Coroutine = loggingOnAssignroleDelete(PhaazeDiscord, GuildSettings,
		Deleter=CheckMember,
		assign_role_trigger=AssignRoleToDelete.trigger,
	)
	asyncio.ensure_future(log_coro, loop=cls.Web.BASE.DiscordLoop)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Assignroles: {guild_id=} deleted [{role_id}, {assignrole_id=}]", require="discord:role")
	return cls.response(
		text=json.dumps( dict(msg="Assignroles: Deleted entry", deleted=AssignRoleToDelete.trigger, status=200) ),
		content_type="application/json",
		status=200
	)
