from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import PhaazeWebIndex

from aiohttp.web import Response
from Utils.Classes.htmlformatter import HTMLFormatter
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.authwebuser import AuthWebUser
from Platforms.Web.index import PhaazeWebIndex
from Platforms.Web.utils import getNavbar, authWebUser

@PhaazeWebIndex.get("/admin/manage-user")
async def adminManageUser(cls:"PhaazeWebIndex", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /admin/manage-user
	"""
	WebAuth:AuthWebUser = await authWebUser(cls, WebRequest)
	if not WebAuth.found:
		return await cls.Tree.Account.accountlogin.accountLogin(WebRequest)
	if not WebAuth.User.checkRoles(["admin", "superadmin"]):
		return await cls.Tree.errors.notAllowed(WebRequest, msg="Admin rights required")

	AdminManageUser:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Admin/manage-user.html")

	site:str = cls.HTMLRoot.replace(
		replace_empty=True,

		title="Phaaze | Admin - User manager",
		header=getNavbar(),
		main=AdminManageUser
	)

	return cls.response(
		body=site,
		status=200,
		content_type='text/html'
	)
