from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

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
