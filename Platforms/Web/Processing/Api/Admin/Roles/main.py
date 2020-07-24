from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

from aiohttp.web import Response, Request
from Utils.Classes.webuserinfo import WebUserInfo
from Platforms.Web.Processing.Api.errors import (
	apiNotAllowed,
	apiMissingValidMethod
)
from .create import apiAdminRolesCreate
from .delete import apiAdminRolesDelete
from .edit import apiAdminRolesEdit
from .get import apiAdminRolesGet

async def apiAdminRoles(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/admin/roles
	"""
	WebUser:WebUserInfo = await cls.getWebUserInfo(WebRequest)
	if not WebUser.checkRoles(["admin", "superadmin"]): return await apiNotAllowed(cls, WebRequest, msg="Admin rights required")

	method:str = WebRequest.match_info.get("method", "")
	if not method: return await apiMissingValidMethod(cls, WebRequest)

	elif method == "get":
		return await apiAdminRolesGet(cls, WebRequest)

	elif method == "edit":
		return await apiAdminRolesEdit(cls, WebRequest)

	elif method == "create":
		return await apiAdminRolesCreate(cls, WebRequest)

	elif method == "delete":
		return await apiAdminRolesDelete(cls, WebRequest)

	else: return await apiMissingValidMethod(cls, WebRequest, msg=f"'{method}' is not a known method")
