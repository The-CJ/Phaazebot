from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

from aiohttp.web import Response, Request
from Utils.Classes.htmlformatter import HTMLFormatter
from Utils.Classes.webuserinfo import WebUserInfo
from Platforms.Web.utils import getNavbar

async def adminManageUser(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /admin/manage-user
	"""
	WebUser:WebUserInfo = await cls.getWebUserInfo(WebRequest)
	if not WebUser.found: return await cls.accountLogin(WebRequest)
	if not WebUser.checkRoles(["admin", "superadmin"]): return await cls.notAllowed(WebRequest, msg="Admin rights required")

	AdminManageUser:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Admin/manage-user.html")

	site:str = cls.HTMLRoot.replace(
		replace_empty = True,

		title = "Phaaze | Admin - User manager",
		header = getNavbar(),
		main = AdminManageUser
	)

	return cls.response(
		body=site,
		status=200,
		content_type='text/html'
	)
