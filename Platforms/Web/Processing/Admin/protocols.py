from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

from aiohttp.web import Response, Request
from Utils.Classes.htmlformatter import HTMLFormatter
from Utils.Classes.webuserinfo import WebUserInfo
from Platforms.Web.utils import getNavbar

async def adminProtocols(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /admin/protocols
	"""
	WebUser:WebUserInfo = await cls.getWebUserInfo(WebRequest)
	if not WebUser.found: return await cls.accountLogin(WebRequest)
	if not WebUser.checkRoles(["superadmin"]): return await cls.notAllowed(WebRequest, msg="Superadmin rights required")

	AdminProtocols:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Admin/protocols.html")

	site:str = cls.HTMLRoot.replace(
		replace_empty = True,

		title = "Phaaze | Admin - Protocols",
		header = getNavbar(),
		main = AdminProtocols
	)

	return cls.response(
		body=site,
		status=200,
		content_type='text/html'
	)
