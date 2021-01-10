from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.discordwebuser import DiscordWebUserInfo
from Platforms.Discord.db import getDiscordServerExceptionRoles, getDiscordServerExceptionRoleAmount
from Platforms.Web.Processing.Api.errors import (
	apiMissingAuthorisation,
	apiMissingData
)
from Platforms.Web.Processing.Api.Discord.errors import (
	apiDiscordGuildUnknown,
	apiDiscordMemberNotFound,
	apiDiscordMissingPermission
)

DEFAULT_LIMIT:int = 50
MAX_LIMIT:int = 100

async def apiDiscordConfigsExceptionRolesGet(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/configs/exceptionroles/get
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	exceptionrole_id:str = Data.getStr("exceptionrole_id", "", must_be_digit=True)
	role_id:str = Data.getStr("role_id", "", must_be_digit=True)
	limit:int = Data.getInt("limit", DEFAULT_LIMIT, min_x=1, max_x=MAX_LIMIT)
	offset:int = Data.getInt("offset", 0, min_x=0)

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

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

	role_res:list = await getDiscordServerExceptionRoles(PhaazeDiscord, guild_id, exceptionrole_id=exceptionrole_id, role_id=role_id, limit=limit, offset=offset)

	return cls.response(
		text=json.dumps( dict(
			result=[ Role.toJSON() for Role in role_res ],
			limit=limit,
			offset=offset,
			total=(await getDiscordServerExceptionRoleAmount(PhaazeDiscord, guild_id)),
			status=200)
		),
		content_type="application/json",
		status=200
	)
