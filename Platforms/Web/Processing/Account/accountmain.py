from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

from aiohttp.web import Response, Request
from Utils.Classes.htmlformatter import HTMLFormatter
from Utils.Classes.webuserinfo import WebUserInfo
from Platforms.Web.utils import getNavbar

async def accountMain(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /account
	"""
	WebUser:WebUserInfo = await cls.getWebUserInfo(WebRequest)
	if not WebUser.found: return await cls.accountLogin(WebRequest)

	AccountPage:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Account/main.html")

	site:str = cls.HTMLRoot.replace(
		replace_empty = True,

		title = "Phaaze | Account",
		header = getNavbar(),
		main = AccountPage
	)

	return cls.response(
		body=site,
		status=200,
		content_type='text/html'
	)
