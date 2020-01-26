from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

from aiohttp.web import Response, Request
from Utils.Classes.htmlformatter import HTMLFormatter
from Utils.Classes.webuserinfo import WebUserInfo
from Platforms.Web.utils import getNavbar

async def accountCreate(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /account/create
	"""
	# already logged in
	WebUser:WebUserInfo = await cls.getWebUserInfo(WebRequest)
	if WebUser.found: return await cls.accountMain(WebRequest)

	CreatePage:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Account/create.html")

	site:str = cls.HTMLRoot.replace(
		replace_empty = True,

		title = "Phaaze | Account - Create",
		header = getNavbar(),
		main = CreatePage
	)

	return cls.response(
		body=site,
		status=200,
		content_type='text/html'
	)
