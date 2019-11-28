from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

from aiohttp.web import Response, Request
from Platforms.Web.Processing.Api.errors import apiMissingValidMethod, apiNotAllowed

async def apiAdminUsers(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/admin/users
	"""
	WebUser:WebUserInfo = await cls.getWebUserInfo(WebRequest)
	if not WebUser.checkRoles(["admin", "superadmin"]): return await apiNotAllowed(cls, WebRequest, msg="Admin rights required")

	method:str = WebRequest.match_info.get("method", "")
	if not method: return await apiMissingValidMethod(cls, WebRequest)

	elif method == "get":
		pass
		# return await apiAdminRolesGet(cls, WebRequest)

	elif method == "edit":
		pass
		# return await apiAdminRolesEdit(cls, WebRequest)

	elif method == "create":
		pass
		# return await apiAdminRolesCreate(cls, WebRequest)

	elif method == "delete":
		pass
		# return await apiAdminRolesDelete(cls, WebRequest)

	else: return await apiMissingValidMethod(cls, WebRequest, msg=f"'{method}' is not a known method")
