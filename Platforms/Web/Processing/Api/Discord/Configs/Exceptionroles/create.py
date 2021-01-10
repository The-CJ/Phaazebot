from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.discordwebuser import DiscordWebUserInfo
from Platforms.Discord.utils import getDiscordRoleFromString
from Platforms.Web.Processing.Api.errors import apiMissingAuthorisation, apiMissingData
from Platforms.Web.Processing.Api.Discord.errors import (
	apiDiscordGuildUnknown,
	apiDiscordMemberNotFound,
	apiDiscordMissingPermission,
	apiDiscordRoleNotFound
)
from .errors import apiDiscordExceptionRoleExists

async def apiDiscordConfigsExceptionRolesCreate(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/configs/exceptionroles/create
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	role_id:str = Data.getStr("role_id", "", must_be_digit=True)

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not role_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'role_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

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

	ActionRole:discord.Role = getDiscordRoleFromString(PhaazeDiscord, Guild, role_id)
	if not ActionRole:
		return await apiDiscordRoleNotFound(cls, WebRequest, guild_id=Guild.id, guild_name=Guild.name, role_id=role_id)

	# check if already exists
	res:list = cls.Web.BASE.PhaazeDB.selectQuery("""
		SELECT COUNT(*) AS `match`
		FROM `discord_blacklist_whitelistrole`
		WHERE `discord_blacklist_whitelistrole`.`guild_id` = %s
			AND `discord_blacklist_whitelistrole`.`role_id` = %s""",
		( guild_id, role_id )
	)

	if res[0]["match"]:
			return await apiDiscordExceptionRoleExists(cls, WebRequest, role_id=role_id, role_name=ActionRole.name)

	cls.Web.BASE.PhaazeDB.insertQuery(
		table = "discord_blacklist_whitelistrole",
		content = {
			"guild_id": guild_id,
			"role_id": role_id
		}
	)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Exceptionrole: {guild_id=} added: {role_id=}", require="discord:configs")
	return cls.response(
		text=json.dumps( dict(msg="Exceptionrole: Added new entry", entry=role_id, status=200) ),
		content_type="application/json",
		status=200
	)
