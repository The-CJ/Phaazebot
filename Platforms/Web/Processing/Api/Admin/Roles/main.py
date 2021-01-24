from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

from aiohttp.web import Response
from Utils.Classes.authwebuser import AuthWebUser
from Utils.Classes.extendedrequest import ExtendedRequest
from Platforms.Web.Processing.Api.errors import apiMissingValidMethod
from Platforms.Web.index import PhaazeWebIndex
from Platforms.Web.utils import authWebUser

@PhaazeWebIndex.view("/api/admin/roles{x:/?}{method:.*}")
async def apiAdminRoles(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/admin/roles{x:/?}{method:.*}
	"""
	WebAuth:AuthWebUser = await authWebUser(cls, WebRequest)
	if not WebAuth.found:
		return await cls.Tree.Api.errors.apiMissingAuthorisation(WebRequest)
	if not WebAuth.User.checkRoles(["admin", "superadmin"]):
		return await cls.Tree.Api.errors.apiNotAllowed(WebRequest, msg="Admin rights required")

	method:str = WebRequest.match_info.get("method", "")
	if not method: return await apiMissingValidMethod(cls, WebRequest)

	elif method == "get":
		return await cls.Tree.Api.Admin.Roles.get.apiAdminRolesGet(cls, WebRequest)

	elif method == "edit":
		return await cls.Tree.Api.Admin.Roles.edit.apiAdminRolesEdit(cls, WebRequest)

	elif method == "create":
		return await cls.Tree.Api.Admin.Roles.create.apiAdminRolesCreate(cls, WebRequest)

	elif method == "delete":
		return await cls.Tree.Api.Admin.Roles.delete.apiAdminRolesDelete(cls, WebRequest)

	else: return await apiMissingValidMethod(cls, WebRequest, msg=f"'{method}' is not a known method")
