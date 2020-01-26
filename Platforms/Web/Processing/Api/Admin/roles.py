from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.webuserinfo import WebUserInfo
from Utils.Classes.webrole import WebRole
from Utils.Classes.undefined import UNDEFINED
from Utils.dbutils import validateDBInput
from Platforms.Web.Processing.Api.errors import (
	apiNotAllowed,
	apiMissingValidMethod,
	apiMissingData,
	apiWrongData
)

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

	# get required stuff
	role_id:int = Data.getInt("role_id", UNDEFINED, min_x=1)

	sql:str = "SELECT * FROM `role`"
	values:tuple = ()

	# only show one?
	if role_id:
		sql += " WHERE `role`.`id` = %s"
		values += (role_id,)

	res:list = cls.Web.BASE.PhaazeDB.selectQuery(sql, values)
	res = [WebRole(r) for r in res]

	return_list:list = list()

	for Role in res:
		return_list.append( Role.toJSON() )

	return cls.response(
		text=json.dumps( dict(result=return_list, status=200) ),
		content_type="application/json",
		status=200
	)

async def apiAdminRolesEdit(cls:"WebIndex", WebRequest:Request) -> Response:
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	role_id:int = Data.getInt("role_id", UNDEFINED, min_x=1)

	# checks
	if not role_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'role_id'")

	res:list = cls.Web.BASE.PhaazeDB.selectQuery(
		"SELECT * FROM `role` WHERE `role`.`id` = %s",
		(role_id,)
	)

	if not res:
		return await apiWrongData(cls, WebRequest, msg=f"could not find role")

	CurrentRole:WebRole = WebRole( res.pop(0) )

	db_changes:dict = dict()
	changes:dict = dict()

	# name
	value:str = Data.getStr("name", UNDEFINED)
	if value != UNDEFINED:
		# only allow role name change as long the role is removable,
		# because based on name... a rename whould be a delete... got it?
		if CurrentRole.can_be_removed:
			db_changes["name"] = validateDBInput(str, value)
			changes["name"] = value

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
		return await apiMissingData(cls, WebRequest, msg="No changes, please add at least one")

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

	# get required stuff
	name:str = Data.getStr("name", "")
	description:str = Data.getStr("description", "")
	can_be_removed:bool = Data.getBool("can_be_removed", True)

	# checks
	if not name:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'name'")

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
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	role_id:int = Data.getInt("role_id", UNDEFINED, min_x=1)

	# checks
	if not role_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'role_id'")

	res:list = cls.Web.BASE.PhaazeDB.selectQuery(
		"SELECT `name`, `can_be_removed` FROM `role` WHERE `role`.`id` = %s",
		(role_id,)
	)

	if not res:
		return await apiWrongData(cls, WebRequest, msg=f"could not find role")

	role:dict = res.pop(0)

	if not role["can_be_removed"]:
		return await apiWrongData(cls, WebRequest, msg=f"'{role['name']}' cannot be removed")

	cls.Web.BASE.PhaazeDB.deleteQuery(
		"DELETE FROM `role` WHERE `role`.`id` = %s",
		(role_id,)
	)

	return cls.response(
		text=json.dumps( dict(msg="role successfull deleted", role=role['name'], status=200) ),
		content_type="application/json",
		status=200
	)
