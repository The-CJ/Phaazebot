from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from .errors import apiNotAllowed, apiMissingAuthorisation
from aiohttp.web import Response, Request
from Utils.Classes.webuserinfo import WebUserInfo

async def apiAccountPhaazeGet(cls:"WebIndex", WebRequest:Request) -> Response:
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

async def apiAccountDiscordGet(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/discord/get
	"""
	return await apiNotAllowed(cls, WebRequest, msg="Under construction")

async def apiAccountTwitchGet(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/twitch/get
	"""
	return await apiNotAllowed(cls, WebRequest, msg="Under construction")
