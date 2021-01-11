from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.discordwebuser import DiscordWebUser
from Utils.Classes.discordwhitelistedrole import DiscordWhitelistedRole
from Platforms.Discord.db import getDiscordServerExceptionRoles
from Platforms.Web.Processing.Api.errors import (
	apiMissingAuthorisation,
	apiMissingData
)
from Platforms.Web.Processing.Api.Discord.errors import (
	apiDiscordGuildUnknown,
	apiDiscordMemberNotFound,
	apiDiscordMissingPermission
)
from .errors import apiDiscordExceptionRoleNotExists

async def apiDiscordConfigsExceptionRolesDelete(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/configs/exceptionroles/delete
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	exceptionrole_id:str = Data.getStr("exceptionrole_id", "", must_be_digit=True)
	role_id:str = Data.getStr("role_id", "", must_be_digit=True)

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if (not exceptionrole_id) and (not role_id):
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'exceptionrole_id' or 'role_id'")

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
	res_words:list = await getDiscordServerExceptionRoles(cls.Web.BASE.Discord, guild_id, exceptionrole_id=exceptionrole_id, role_id=role_id)

	if not res_words:
		return await apiDiscordExceptionRoleNotExists(cls, WebRequest, exceptionrole_id=exceptionrole_id, role_id=role_id)

	RoleToDelete:DiscordWhitelistedRole = res_words.pop(0)

	cls.Web.BASE.PhaazeDB.deleteQuery("""
		DELETE FROM `discord_blacklist_whitelistrole` WHERE `guild_id` = %s AND `id` = %s""",
		(RoleToDelete.guild_id, RoleToDelete.exceptionrole_id)
	)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Exceptionrole: {guild_id=} deleted [{exceptionrole_id=}, {role_id=}]", require="discord:configs")
	return cls.response(
		text=json.dumps( dict(msg=f"Exceptionrole: Deleted entry", deleted=RoleToDelete.role_id, status=200) ),
		content_type="application/json",
		status=200
	)
