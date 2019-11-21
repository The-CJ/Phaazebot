from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from main import Phaazebot

import json
import time
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.webuserinfo import WebUserInfo
from ..errors import apiNotAllowed, apiMissingValidMethod

async def apiAdminRole(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/admin/roles
	"""
	WebUser:WebUserInfo = await cls.getWebUserInfo(WebRequest)
	if not WebUser.checkRoles(["admin", "superadmin"]): return await apiNotAllowed(cls, WebRequest, msg="Admin rights required")

	method:str = WebRequest.match_info.get("method", "")
	if not method: return await apiMissingValidMethod(cls, WebRequest)

	elif method == "get":
		return await apiAdminRoleGet(cls, WebRequest)

	elif method == "edit":
		return await apiAdminRoleEdit(cls, WebRequest)

	elif method == "create":
		return await apiAdminRoleCreate(cls, WebRequest)

	elif method == "delete":
		return await apiAdminRoleDelete(cls, WebRequest)

	else: return await apiMissingValidMethod(cls, WebRequest, msg=f"'{method}' is not a known method")

async def apiAdminRoleGet(cls:"WebIndex", WebRequest:Request) -> Response:
	pass

async def apiAdminRoleEdit(cls:"WebIndex", WebRequest:Request) -> Response:
	pass

async def apiAdminRoleCreate(cls:"WebIndex", WebRequest:Request) -> Response:
	pass

async def apiAdminRoleDelete(cls:"WebIndex", WebRequest:Request) -> Response:
	pass
