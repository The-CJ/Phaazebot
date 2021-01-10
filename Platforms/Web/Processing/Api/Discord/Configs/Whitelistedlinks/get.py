from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.discordwebuser import DiscordWebUserInfo
from Platforms.Discord.db import getDiscordServerWhitelistedLinks, getDiscordServerWhitelistedLinkAmount
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

async def apiDiscordConfigsWhitelistedLinkGet(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/configs/whitelistedlinks/get
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	link_id:str = Data.getStr("link_id", "", must_be_digit=True)
	link:str = Data.getStr("link", "")
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

	link_res:list = await getDiscordServerWhitelistedLinks(PhaazeDiscord, guild_id, link_id=link_id, link=link, limit=limit, offset=offset)

	return cls.response(
		text=json.dumps( dict(
			result=[ Link.toJSON() for Link in link_res ],
			limit=limit,
			offset=offset,
			total=(await getDiscordServerWhitelistedLinkAmount(PhaazeDiscord, guild_id)),
			status=200)
		),
		content_type="application/json",
		status=200
	)
