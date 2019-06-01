from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

from .errors import apiNotAllowed, userNotFound, missingData
from aiohttp.web import Response, Request
from Utils.Classes.webuserinfo import WebUserInfo

async def apiAccountPhaazeLogin(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/phaaze/login
		looks like all other UserInfo pairs, except this time it should be a post request, leading new information to login,
		create session and give this to the user
	"""
	UserInfo:WebUserInfo = await cls.getUserInfo(WebRequest)

	if not UserInfo.tryed:
		return await missingData(cls, WebRequest)

	if not UserInfo.found:
		return await userNotFound(cls, WebRequest)

async def apiAccountDiscordLogin(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/discord/login
		This sould only be called by discord after a user successfull authorised
	"""
	return await apiNotAllowed(cls, WebRequest, msg="Under construction")

async def apiAccountTwitchLogin(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/twitch/login
		This sould only be called by twitch after a user successfull authorised
	"""
	return await apiNotAllowed(cls, WebRequest, msg="Under construction")
