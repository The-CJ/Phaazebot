from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.webrole import WebRole
from Utils.Classes.webuserinfo import WebUserInfo
from Utils.Classes.undefined import UNDEFINED
from Utils.dbutils import validateDBInput
from Utils.stringutils import password as password_function
from Platforms.Web.utils import getWebUsers
from Platforms.Web.Processing.Api.errors import (
	apiMissingData,
	apiWrongData,
	apiNotAllowed,
	apiUserNotFound
)

async def apiAdminUsersEdit(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/admin/users/edit
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	user_id:str = Data.getStr("user_id", "", must_be_digit=True)

	# checks
	if not user_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'user_id'")

	# single actions
	action:str = Data.getStr("userrole_action", UNDEFINED)
	if action:
		return await singleActionUserRole(cls, WebRequest, action, Data)

	# get user that should be edited
	check_user:list = await getWebUsers(cls, where="user.id = %s", values=(user_id,))
	if not check_user:
		return await apiUserNotFound(cls, WebRequest, msg=f"no user found with id: {user_id}")

	# check if this is a (super)admin, if so, is the current user a superadmin?
	# and not himself
	UserToEdit:WebUserInfo = check_user.pop(0)
	CurrentUser:WebUserInfo = await cls.getWebUserInfo(WebRequest)
	if UserToEdit.checkRoles(["superadmin", "admin"]):
		if UserToEdit.user_id != CurrentUser.user_id:
			if not CurrentUser.checkRoles(["superadmin"]):
				return await apiNotAllowed(cls, WebRequest, msg=f"Only Superadmin's can edit other (Super)admin user")

	# check all update values
	update:dict = dict()
	db_update:dict = dict()

	# username
	value:str = Data.getStr("username", UNDEFINED)
	if value != UNDEFINED:
		db_update["username"] = validateDBInput(str, value)
		update["username"] = value

	# email
	value:str = Data.getStr("email", UNDEFINED)
	if value != UNDEFINED:
		db_update["email"] = validateDBInput(str, value)
		update["email"] = value

	# password
	value:str = Data.getStr("password", UNDEFINED)
	if value: # aka non empty string and not UNDEFINED
		value = password_function(value)
		db_update["password"] = validateDBInput(str, value)
		update["password"] = value

	# verified
	value:bool = Data.getBool("verified", UNDEFINED)
	if value != UNDEFINED:
		db_update["verified"] = validateDBInput(bool, value)
		update["verified"] = value

	if not db_update:
		return await apiMissingData(cls, WebRequest, msg="No changes, please add at least one")

	cls.Web.BASE.Logger.debug(f"(API) Config User U:{user_id} {str(db_update)}", require="api:user")
	cls.Web.BASE.PhaazeDB.updateQuery(
		table = "user",
		content = db_update,
		where = "`user`.`id` = %s",
		where_values = (user_id,)
	)

	return cls.response(
		text=json.dumps( dict(msg="user successfull updated", update=update, status=200) ),
		content_type="application/json",
		status=200
	)

async def singleActionUserRole(cls:"WebIndex", WebRequest:Request, action:str, Data:WebRequestContent) -> Response:
	"""
		Default url: /api/admin/users/edit?userrole_action=something
	"""
	user_id:str = Data.getStr("user_id", "")
	action = action.lower()
	userrole_role:str = Data.getStr("userrole_role", "")

	if not user_id:
		# should never happen
		return await apiMissingData(cls, WebRequest, msg="missing field 'user_id'")

	if not userrole_role:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid field 'userrole_role'")

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

	# prevent role missabuse
	if Role.name.lower() in ["superadmin", "admin"]:
		if not ( await cls.getWebUserInfo(WebRequest) ).checkRoles(["superadmin"]):
			return await apiNotAllowed(cls, WebRequest, msg=f"Only Superadmin's can assign/remove '{Role.name}' to user")

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
			cls.Web.BASE.PhaazeDB.deleteQuery("""
				DELETE FROM `user_has_role`
				WHERE `role_id` = %s
					AND `user_id` = %s""",
				(Role.role_id, user_id)
			)

			return cls.response(
				text=json.dumps( dict(msg="user roles successfull updated", rem=Role.name, status=200) ),
				content_type="application/json",
				status=200
			)
		except:
			return await apiWrongData(cls, WebRequest, msg=f"user don't has role: '{Role.name}'")

	else:
		return await apiWrongData(cls, WebRequest)
