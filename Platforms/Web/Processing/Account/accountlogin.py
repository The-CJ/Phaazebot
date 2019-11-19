from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

from aiohttp.web import Response, Request
from Utils.Classes.htmlformatter import HTMLFormatter
from Utils.Classes.webuserinfo import WebUserInfo
from Platforms.Web.utils import getNavbar

async def accountLogin(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /account/login
	"""
	WebUser:WebUserInfo = await cls.getWebUserInfo(WebRequest)
	if WebUser.found: return await cls.accountMain(WebRequest)

	AccountLogin:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Account/login.html")

	site:str = cls.HTMLRoot.replace(
		replace_empty = True,

		title = "Phaaze | Account - Login",
		header = getNavbar(),
		main = AccountLogin
	)

	return cls.response(
		body=site,
		status=200,
		content_type='text/html'
	)
