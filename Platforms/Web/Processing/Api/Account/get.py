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
		username=str( UserInfo.username ),
		email=str( UserInfo.email ),
		verified=bool( UserInfo.verified ),
		roles=list( UserInfo.roles ),
		user_id=int( UserInfo.user_id ),
		last_login=str( UserInfo.last_login )
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
		username=str( DiscordUser.username ),
		verified=bool( DiscordUser.verified ),
		locale=str( DiscordUser.locale ),
		premium_type=str( DiscordUser.premium_type ),
		user_id=str( DiscordUser.user_id ),
		flags=str( DiscordUser.flags ),
		avatar=str( DiscordUser.avatar ),
		discriminator=str( DiscordUser.discriminator ),
		email=str( DiscordUser.email )
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
