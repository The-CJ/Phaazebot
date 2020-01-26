from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

from aiohttp.web import Response, Request
from Utils.Classes.htmlformatter import HTMLFormatter
from Utils.Classes.webuserinfo import WebUserInfo
from Platforms.Web.utils import getNavbar

async def adminManageSystem(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /admin/manage-system
	"""
	WebUser:WebUserInfo = await cls.getWebUserInfo(WebRequest)
	if not WebUser.found: return await cls.accountLogin(WebRequest)
	if not WebUser.checkRoles(["admin", "superadmin"]): return await cls.notAllowed(WebRequest, msg="Admin rights required")

	AdminManageSystem:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Admin/manage-system.html")

	site:str = cls.HTMLRoot.replace(
		replace_empty = True,

		title = "Phaaze | Admin - System manager",
		header = getNavbar(),
		main = AdminManageSystem
	)

	return cls.response(
		body=site,
		status=200,
		content_type='text/html'
	)
