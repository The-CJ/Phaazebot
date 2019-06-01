from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

from .errors import apiMissingAuthorisation, apiNotAllowed
from aiohttp.web import Response, Request
from Utils.Classes.webuserinfo import WebUserInfo

async def apiAccountLoginPhaaze(self:"WebIndex", WebRequest:Request) -> Response:
	"""
		looks like all other UserInfo pairs, except this time it should be a post request, leading new information to login,
		create session and give this to the user
	"""
	UserInfo:WebUserInfo = await self.getUserInfo(WebRequest)

	if not UserInfo.found:
		return await apiMissingAuthorisation(self, WebRequest)

async def apiAccountLoginDiscord(self:"WebIndex", WebRequest:Request) -> Response:
	"""
		This sould only be called by discord after a user successfull authorised
	"""
	return await apiNotAllowed(self, WebRequest, msg="Under construction")

async def apiAccountLoginTwitch(self:"WebIndex", WebRequest:Request) -> Response:
	"""
		This sould only be called by twitch after a user successfull authorised
	"""
	return await apiNotAllowed(self, WebRequest, msg="Under construction")
