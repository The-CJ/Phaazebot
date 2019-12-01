from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.webrole import WebRole
from Platforms.Web.Processing.Api.errors import missingData, apiWrongData
from Utils.Classes.undefined import UNDEFINED
from Utils.dbutils import validateDBInput

async def apiAdminUsersEdit(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/admin/users/edit
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	user_id:str = Data.getStr("user_id", "", must_be_digit=True)
	if not user_id:
		return await missingData(cls, WebRequest, msg="missing or invalid 'user_id'")

	# single actions
	action:str = Data.getStr("userrole_action", UNDEFINED)
	if action:
		return await singleActionUserRole(cls, WebRequest, action, Data)

	changes:dict = dict()
	db_changes:dict = dict()

	# username
	value:str = Data.getStr("username", UNDEFINED)
	if value != UNDEFINED:
		db_changes["username"] = validateDBInput(str, value)
		changes["username"] = value

	# email
	value:str = Data.getStr("email", UNDEFINED)
	if value != UNDEFINED:
		db_changes["email"] = validateDBInput(str, value)
		changes["email"] = value

	# verified
	value:bool = Data.getBool("verified", UNDEFINED)
	if value != UNDEFINED:
		db_changes["verified"] = validateDBInput(bool, value)
		changes["verified"] = value

	if not db_changes:
		return await missingData(cls, WebRequest, msg="No changes, please add at least one")

	cls.Web.BASE.Logger.debug(f"(API) Config User U:{user_id} {str(db_changes)}", require="api:user")
	cls.Web.BASE.PhaazeDB.updateQuery(
		table = "user",
		content = db_changes,
		where = "user.id = %s",
		where_values = (user_id,)
	)

	return cls.response(
		text=json.dumps( dict(msg="user successfull updated", changes=changes, status=200) ),
		content_type="application/json",
		status=200
	)

async def singleActionUserRole(cls:"WebIndex", WebRequest:Request, action:str, Data:WebRequestContent) -> Response:
	"""
		Default url: /api/admin/users/edit?userrole_action=something
	"""
	user_id:str = Data.getStr("user_id", "")
	action = action.lower()
	userrole_role:str = Data.getStr("userrole_role", "").strip(" ").strip("\n")

	if not user_id:
		# should never happen
		return await missingData(cls, WebRequest, msg="missing field 'user_id'")

	if not userrole_role:
		return await missingData(cls, WebRequest, msg="missing or invalid field 'userrole_role'")

	# if it's not a number, try to get id from name, else... just select it again... REEEE
	res:list = cls.Web.BASE.PhaazeDB.selectQuery("""
		SELECT *
		FROM `role`
		WHERE LOWER(`role`.`name`) = LOWER(%s)
			OR `role`.`id` = %s""",
		(userrole_role, userrole_role)
	)

	if not res:
		return await apiWrongData(cls, WebRequest, msg=f"role '{userrole_role}' could not be resolved as a role")

	# here we hope there is only one result, in theory there can be more, BUT since this is a admin endpoint,
	# i wont will do much error handling
	Role:WebRole = WebRole(res.pop(0))

	if action == "add":
		try:
			cls.Web.BASE.PhaazeDB.insertQuery(
				table = "user_has_role",
				content = dict(
					user_id = user_id,
					role_id = Role.role_id
				)
			)
			return cls.response(
				text=json.dumps( dict(msg="user roles successfull updated", add=Role.name, status=200) ),
				content_type="application/json",
				status=200
			)
		except:
			return await apiWrongData(cls, WebRequest, msg=f"user already has role: '{Role.name}'")

	elif action == "remove":
		try:
			hits:int = cls.Web.BASE.PhaazeDB.deleteQuery("""
				DELETE FROM `user_has_role`
				WHERE `role_id` = %s
					AND `user_id` = %s""",
				(Role.role_id, user_id)
			)

			if not hits:
				raise RuntimeError()

			return cls.response(
				text=json.dumps( dict(msg="user roles successfull updated", rem=Role.name, status=200) ),
				content_type="application/json",
				status=200
			)
		except:
			return await apiWrongData(cls, WebRequest, msg=f"user don't has role: '{Role.name}'")

	else:
		return await apiWrongData(cls, WebRequest)
