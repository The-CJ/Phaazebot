from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

from .errors import apiMissingAuthorisation, apiNotAllowed, apiMissingValidMethod
from aiohttp.web import Response, Request
from Utils.Classes.webuserinfo import WebUserInfo

async def apiAccountPhaaze(self:"WebIndex", WebRequest:Request) -> Response:
	method:str = WebRequest.match_info.get("method", None)
	if not method: return await apiMissingValidMethod(self, WebRequest)

	UserInfo:WebUserInfo = await self.getUserInfo(WebRequest)

	if not UserInfo.found:
		return await apiMissingAuthorisation(self, WebRequest)

async def apiAccountDiscord(self:"WebIndex", WebRequest:Request) -> Response:
	return await apiNotAllowed(self, WebRequest, msg="Under construction")

async def apiAccountTwitch(self:"WebIndex", WebRequest:Request) -> Response:
	return await apiNotAllowed(self, WebRequest, msg="Under construction")
