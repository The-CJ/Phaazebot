from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from main import Phaazebot

import json
import time
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.webuserinfo import WebUserInfo
from Utils.Classes.webrole import WebRole
from Utils.Classes.undefined import UNDEFINED
from ..errors import apiNotAllowed, apiMissingValidMethod

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

async def apiAdminRolesGet(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/admin/roles/get
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	sql:str = "SELECT * FROM `role`"
	values:tuple = ()

	# only show one?
	role_id:int = Data.getInt("role_id", UNDEFINED, min_x=1)
	if role_id:
		sql += " WHERE `role`.`id` = %s"
		values += (role_id,)

	res:list = cls.Web.BASE.PhaazeDB.selectQuery(sql, values)

	return_list:list = list()
	for r in res:
		Role:WebRole = WebRole(r)
		role:dict = dict(
			id = Role.id,
			name = Role.name,
			description = Role.description if Role.description else "",
			can_be_removed = Role.can_be_removed
		)
		return_list.append( role )

	return cls.response(
		text=json.dumps( dict(result=return_list, status=200) ),
		content_type="application/json",
		status=200
	)

async def apiAdminRolesEdit(cls:"WebIndex", WebRequest:Request) -> Response:
	pass

async def apiAdminRolesCreate(cls:"WebIndex", WebRequest:Request) -> Response:
	pass

async def apiAdminRolesDelete(cls:"WebIndex", WebRequest:Request) -> Response:
	pass
