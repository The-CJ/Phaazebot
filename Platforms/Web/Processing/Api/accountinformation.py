from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

from .errors import apiMissingAuthorisation, apiNotAllowed
from aiohttp.web import Response, Request
from Utils.Classes.webuserinfo import WebUserInfo

async def apiAccountInfoPhaaze(self:"WebIndex", WebRequest:Request) -> Response:
	UserInfo:WebUserInfo = await self.getUserInfo(WebRequest)

	if not UserInfo.found:
		return await apiMissingAuthorisation(self, WebRequest)

async def apiAccountInfoDiscord(self:"WebIndex", WebRequest:Request) -> Response:
	return await apiNotAllowed(self, WebRequest, msg="Under construction")

async def apiAccountInfoTwitch(self:"WebIndex", WebRequest:Request) -> Response:
	return await apiNotAllowed(self, WebRequest, msg="Under construction")
