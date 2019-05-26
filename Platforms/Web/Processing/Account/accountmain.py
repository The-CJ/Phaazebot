from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

from aiohttp.web import Response, Request
from Utils.Classes.webuserinfo import WebUserInfo
from Platforms.Web.utils import getNavbar

async def accountMain(self:"WebIndex", Request:Request) -> Response:
	UserInfo:WebUserInfo = await self.getUserInfo(Request)

	print(vars(UserInfo))

	site:str = self.HTMLRoot.replace(
		replace_empty = True,

		title = "Phaaze | Account",
		header = getNavbar()
	)

	return self.response(
		body=site,
		status=200,
		content_type='text/html'
	)
