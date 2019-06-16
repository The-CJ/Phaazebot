from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request
from Utils.Classes.webuserinfo import WebUserInfo
from ..errors import apiNotAllowed, userNotFound

async def apiAccountLogoutPhaaze(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/phaaze/logout
	"""
	UserInfo:WebUserInfo = await cls.getUserInfo(WebRequest)

	if not UserInfo.found:
		return await userNotFound(cls, WebRequest)

	cls.Web.BASE.PhaazeDB.delete(
		of = "session/phaaze",
		where = f"int(data['user_id']) == int({UserInfo.user_id})",
	)

	cls.Web.BASE.Logger.debug(f"Logout - User: {UserInfo.username}", require="api:logout")
	return cls.response(
		text=json.dumps( dict(status=200) ),
		content_type="application/json",
		status=200
	)

async def apiAccountLogoutDiscord(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/discord/logout
	"""
	return await apiNotAllowed(cls, WebRequest, msg="Under construction")

async def apiAccountLogoutTwitch(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/twitch/logout
	"""
	return await apiNotAllowed(cls, WebRequest, msg="Under construction")
