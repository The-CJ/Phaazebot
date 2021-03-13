from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.main_web import PhaazebotWeb

import json
import discord
from aiohttp.web import Response
from Utils.Classes.discordwhitelistedrole import DiscordWhitelistedRole
from Utils.Classes.authdiscordwebuser import AuthDiscordWebUser
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.extendedrequest import ExtendedRequest
from Platforms.Discord.db import getDiscordServerExceptionRoles
from Platforms.Web.utils import authDiscordWebUser
from Platforms.Web.Processing.Api.errors import apiMissingAuthorisation, apiMissingData

async def apiDiscordConfigsExceptionRolesDelete(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/configs/exceptionroles/delete
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	exceptionrole_id:str = Data.getStr("exceptionrole_id", "", must_be_digit=True)

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not exceptionrole_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'exceptionrole_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await cls.Tree.Api.Discord.errors.apiDiscordGuildUnknown(cls, WebRequest)

	# get user info
	AuthDiscord:AuthDiscordWebUser = await authDiscordWebUser(cls, WebRequest)
	if not AuthDiscord.found:
		return await apiMissingAuthorisation(cls, WebRequest)

	# get member
	CheckMember:discord.Member = Guild.get_member(int(AuthDiscord.User.user_id))
	if not CheckMember:
		return await cls.Tree.Api.Discord.errors.apiDiscordMemberNotFound(cls, WebRequest, guild_id=guild_id, user_id=AuthDiscord.User.user_id)

	# check permissions
	if not (CheckMember.guild_permissions.administrator or CheckMember.guild_permissions.manage_guild):
		return await cls.Tree.Api.Discord.errors.apiDiscordMissingPermission(cls, WebRequest, guild_id=guild_id, user_id=AuthDiscord.User.user_id)

	# get assign roles
	res_words:List[DiscordWhitelistedRole] = await getDiscordServerExceptionRoles(PhaazeDiscord, guild_id=guild_id, exceptionrole_id=exceptionrole_id)

	if not res_words:
		return await cls.Tree.Api.Discord.Configs.Exceptionroles.errors.apiDiscordExceptionRoleNotExists(cls, WebRequest, exceptionrole_id=exceptionrole_id)

	RoleToDelete:DiscordWhitelistedRole = res_words.pop(0)

	cls.BASE.PhaazeDB.deleteQuery("""
		DELETE FROM `discord_blacklist_whitelistrole` WHERE `guild_id` = %s AND `id` = %s""",
		(RoleToDelete.guild_id, RoleToDelete.exceptionrole_id)
	)

	cls.BASE.Logger.debug(f"(API/Discord) Exceptionrole: {guild_id=} deleted {exceptionrole_id=}", require="discord:configs")
	return cls.response(
		text=json.dumps(dict(msg=f"Exceptionrole: Deleted entry", deleted=RoleToDelete.role_id, status=200)),
		content_type="application/json",
		status=200
	)
