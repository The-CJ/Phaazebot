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
from Utils.dbutils import validateDBInput
from ..errors import apiNotAllowed, apiMissingValidMethod, missingData, apiWrongData

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
	res = [WebRole(r) for r in res]

	return_list:list = list()

	for Role in res:
		api_role:dict = dict(
			id = Role.id,
			name = Role.name,
			description = Role.description if Role.description else "",
			can_be_removed = Role.can_be_removed
		)

		return_list.append( api_role )

	return cls.response(
		text=json.dumps( dict(result=return_list, status=200) ),
		content_type="application/json",
		status=200
	)

async def apiAdminRolesEdit(cls:"WebIndex", WebRequest:Request) -> Response:
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	role_id:int = Data.getInt("role_id", UNDEFINED, min_x=1)
	if not role_id:
		return await missingData(cls, WebRequest, msg="missing or invalid 'role_id'")

	db_changes:dict = dict()
	changes:dict = dict()

	# description
	value:str = Data.getStr("description", UNDEFINED)
	if value != UNDEFINED:
		db_changes["description"] = validateDBInput(str, value)
		changes["description"] = value

	# can_be_removed
	value:bool = Data.getBool("can_be_removed", UNDEFINED)
	if value != UNDEFINED:
		# this value can only be set to 0
		# if the user gives a 1, meaning to make it removeable... we just ignore it
		if not value:
			db_changes["can_be_removed"] = validateDBInput(bool, value)
			changes["can_be_removed"] = value

	if not db_changes:
		return await missingData(cls, WebRequest, msg="No changes, please add at least one")

	cls.Web.BASE.Logger.debug(f"(API) Role update: R:{role_id} {str(db_changes)}", require="api:admin")
	cls.Web.BASE.PhaazeDB.updateQuery(
		table = "role",
		content = db_changes,
		where = "role.id = %s",
		where_values = (role_id,)
	)

	return cls.response(
		text=json.dumps( dict(msg="role successfull updated", changes=changes, status=200) ),
		content_type="application/json",
		status=200
	)

async def apiAdminRolesCreate(cls:"WebIndex", WebRequest:Request) -> Response:
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	name:str = Data.getStr("name", "")
	description:str = Data.getStr("description", "")
	can_be_removed:bool = Data.getBool("can_be_removed", True)

	if not name:
		return await missingData(cls, WebRequest, msg="missing or invalid 'name'")

	res:list = cls.Web.BASE.PhaazeDB.selectQuery(
		"SELECT COUNT(*) AS `i` FROM `role` WHERE LOWER(`role`.`name`) = %s",
		(name,)
	)

	if res[0]['i'] != 0:
		return await apiWrongData(cls, WebRequest, msg=f"role '{name}' already exists")

	cls.Web.BASE.PhaazeDB.insertQuery(
		table = "role",
		content = dict(
			name = name,
			description = description,
			can_be_removed = validateDBInput(bool, can_be_removed)
		)
	)

	return cls.response(
		text=json.dumps( dict(msg="role successfull created", role=name, status=200) ),
		content_type="application/json",
		status=200
	)

async def apiAdminRolesDelete(cls:"WebIndex", WebRequest:Request) -> Response:
	pass
