from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from ..errors import apiNotAllowed, apiMissingAuthorisation
from aiohttp.web import Response, Request
from Utils.Classes.webuserinfo import WebUserInfo
from Utils.Classes.discorduserinfo import DiscordUserInfo

async def apiAccountGetPhaaze(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/phaaze/get
	"""
	UserInfo:WebUserInfo = await cls.getUserInfo(WebRequest)

	if not UserInfo.found:
		return await apiMissingAuthorisation(cls, WebRequest)

	user:dict = dict(
		username=UserInfo.username,
		email=UserInfo.email,
		verified=UserInfo.verified,
		roles=UserInfo.roles,
		role_ids=UserInfo.role_ids,
		user_id=UserInfo.user_id,
		last_login=UserInfo.last_login
	)

	return cls.response(
		text=json.dumps( dict(user=user,status=200) ),
		content_type="application/json",
		status=200
	)

async def apiAccountGetDiscord(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/discord/get
	"""
	DiscordUser:DiscordUserInfo = await cls.getDiscordUserInfo(WebRequest)

	if not DiscordUser.found:
		return await apiMissingAuthorisation(cls, WebRequest)

	user:dict = dict(
		username=DiscordUser.username,
		verified=DiscordUser.verified,
		locale=DiscordUser.locale,
		premium_type=DiscordUser.premium_type,
		user_id=DiscordUser.user_id,
		flags=DiscordUser.flags,
		avatar=DiscordUser.avatar,
		discriminator=DiscordUser.discriminator,
		email=DiscordUser.email
	)

	return cls.response(
		text=json.dumps( dict(user=user,status=200) ),
		content_type="application/json",
		status=200
	)

async def apiAccountGetTwitch(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/twitch/get
	"""
	return await apiNotAllowed(cls, WebRequest, msg="Under construction")
