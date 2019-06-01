from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

from .errors import apiMissingAuthorisation, apiNotAllowed, apiMissingValidMethod
from aiohttp.web import Response, Request
from Utils.Classes.webuserinfo import WebUserInfo

async def apiAccountPhaaze(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/phaaze
	"""
	method:str = WebRequest.match_info.get("method", None)
	if not method: return await apiMissingValidMethod(cls, WebRequest)

	UserInfo:WebUserInfo = await cls.getUserInfo(WebRequest)

	if not UserInfo.found:
		return await apiMissingAuthorisation(cls, WebRequest)

async def apiAccountDiscord(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/discord
	"""
	return await apiNotAllowed(cls, WebRequest, msg="Under construction")

async def apiAccountTwitch(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/twitch
	"""
	return await apiNotAllowed(cls, WebRequest, msg="Under construction")
