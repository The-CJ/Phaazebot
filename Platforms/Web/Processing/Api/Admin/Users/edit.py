from typing import TYPE_CHECKING, List, Dict, Any
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.authwebuser import AuthWebUser
from Utils.Classes.webrole import WebRole
from Utils.Classes.undefined import UNDEFINED
from Utils.dbutils import validateDBInput
from Utils.stringutils import passwordToHash as password_function
from Platforms.Web.db import getWebUsers, getWebRoles
from Platforms.Web.Processing.Api.errors import (
	apiMissingData,
	apiNotAllowed,
	apiUserNotFound,
	apiWrongData
)
from Platforms.Web.Processing.Api.Admin.Roles.errors import apiAdminRoleNotExists

async def apiAdminUsersEdit(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
	Default url: /api/admin/users/edit
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	user_id:int = Data.getInt("user_id", 0, min_x=1)
	operation:str = Data.getStr("operation", UNDEFINED, len_max=128)

	# checks
	if not user_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'user_id'")

	# get user that should be edited
	check_user:List[AuthWebUser] = await getWebUsers(cls, user_id=user_id)
	if not check_user:
		return await apiUserNotFound(cls, WebRequest, user_id=user_id)

	# check if this is a (super)admin, if so, is the current user a superadmin?
	# and not himself
	UserToEdit:AuthWebUser = check_user.pop(0)
	CurrentUser:AuthWebUser = await cls.getWebUserInfo(WebRequest)
	if UserToEdit.checkRoles(["superadmin", "admin"]):
		if UserToEdit.user_id != CurrentUser.user_id:
			if not CurrentUser.checkRoles(["superadmin"]):
				return await apiNotAllowed(cls, WebRequest, msg=f"Only Superadmin's can edit other (Super)admin user")

	# single action operations
	if operation == "addrole":
		return await apiAdminUsersOperationAddrole(cls, WebRequest, Data, UserToEdit, CurrentUser)
	if operation == "removerole":
		return await apiAdminUsersOperationRemoverole(cls, WebRequest, Data, UserToEdit, CurrentUser)

	# check all update values
	update:Dict[str, Any] = dict()
	db_update:[str, Any] = dict()

	# username
	value:str = Data.getStr("username", UNDEFINED, len_max=64)
	if value != UNDEFINED:
		db_update["username"] = validateDBInput(str, value)
		update["username"] = value

	# email
	value:str = Data.getStr("email", UNDEFINED, len_max=128)
	if value != UNDEFINED:
		db_update["email"] = validateDBInput(str, value)
		update["email"] = value

	# password
	value:str = Data.getStr("password", UNDEFINED, len_max=256)
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

async def apiAdminUsersOperationAddrole(cls:"WebIndex", WebRequest:Request, Data:WebRequestContent, EditUser:AuthWebUser, CurrentUser:AuthWebUser) -> Response:
	"""
	Default url: /api/admin/users?operation=addrole
	"""
	# get required stuff
	role_id:int = Data.getInt("role_id", 0, min_x=1)

	# checks
	if not role_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'role_id'")

	res:List[WebRole] = await getWebRoles(cls, role_id=role_id)
	if not res:
		return await apiAdminRoleNotExists(cls, WebRequest, role_id=role_id)

	WantedRole:WebRole = res.pop(0)

	if EditUser.checkRoles(WantedRole.name):
		return await apiWrongData(cls, WebRequest, msg=f"{EditUser.username} already has role: {WantedRole.name}")

	if WantedRole.name.lower() in ["superadmin", "admin"]:
		if not ( CurrentUser.checkRoles("superadmin") ):
			return await apiNotAllowed(cls, WebRequest, msg=f"Only Superadmin's can assign/remove {WantedRole.name} to user")

	cls.Web.BASE.PhaazeDB.insertQuery(
		table="user_has_role",
		content={"user_id":EditUser.user_id, "role_id":WantedRole.role_id}
	)

	return cls.response(
		text=json.dumps( dict(msg="User: added role", add=WantedRole.name, status=200) ),
		content_type="application/json",
		status=200
	)

async def apiAdminUsersOperationRemoverole(cls:"WebIndex", WebRequest:Request, Data:WebRequestContent, EditUser:AuthWebUser, CurrentUser:AuthWebUser) -> Response:
	"""
	Default url: /api/admin/users?operation=removerole
	"""
	# get required stuff
	role_id:int = Data.getInt("role_id", 0, min_x=1)

	# checks
	if not role_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'role_id'")

	res:List[WebRole] = await getWebRoles(cls, role_id=role_id)
	if not res:
		return await apiAdminRoleNotExists(cls, WebRequest, role_id=role_id)

	UnwantedRole:WebRole = res.pop(0)

	if not EditUser.checkRoles(UnwantedRole.name):
		return await apiWrongData(cls, WebRequest, msg=f"{EditUser.username} don't have role: {UnwantedRole.name}")

	if UnwantedRole.name.lower() in ["superadmin", "admin"]:
		if not ( CurrentUser.checkRoles("superadmin") ):
			return await apiNotAllowed(cls, WebRequest, msg=f"Only Superadmin's can assign/remove {UnwantedRole.name} to user")

	cls.Web.BASE.PhaazeDB.deleteQuery("""
		DELETE FROM `user_has_role`
		WHERE `user_id` = %s
			AND `role_id` = %s""",
		(EditUser.user_id, UnwantedRole.role_id)
	)

	return cls.response(
		text=json.dumps( dict(msg="User: removed role", remove=UnwantedRole.name, status=200) ),
		content_type="application/json",
		status=200
	)
