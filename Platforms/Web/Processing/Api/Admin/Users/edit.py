from typing import TYPE_CHECKING, List, Dict, Any
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

import json
from aiohttp.web import Response
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.storagetransformer import StorageTransformer
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.authwebuser import AuthWebUser
from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.webrole import WebRole
from Utils.Classes.webuser import WebUser
from Utils.stringutils import passwordToHash as passwordFunction
from Platforms.Web.db import getWebUsers, getWebRoles
from Platforms.Web.utils import authWebUser

async def apiAdminUsersEdit(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/admin/users/edit
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	Edit:StorageTransformer = StorageTransformer()
	Edit["user_id"] = Data.getInt("user_id", 0, min_x=1)
	Edit["operation"] = Data.getStr("operation", UNDEFINED, len_max=128)

	# checks
	if not Edit["user_id"]:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'user_id'")

	# get user that should be edited
	check_user:List[WebUser] = await getWebUsers(cls, user_id=Edit["user_id"])
	if not check_user:
		return await cls.Tree.Api.errors.apiUserNotFound(cls, WebRequest, user_id=Edit["user_id"])

	# check if this is a (super)admin, if so, is the current user a superadmin?
	# and not himself
	UserToEdit:WebUser = check_user.pop(0)
	CurrentUserAuth:AuthWebUser = await authWebUser(cls, WebRequest)
	if UserToEdit.checkRoles(["superadmin", "admin"]):
		if UserToEdit.user_id != CurrentUserAuth.User.user_id:
			if not CurrentUserAuth.User.checkRoles(["superadmin"]):
				return await cls.Tree.Api.errors.apiNotAllowed(cls, WebRequest, msg=f"Only Superadmin's can edit other (Super)admin user")

	# single action operations
	if Edit["operation"] == "addrole":
		return await apiAdminUsersOperationAddrole(cls, WebRequest, Data, UserToEdit, CurrentUserAuth.User)
	if Edit["operation"] == "removerole":
		return await apiAdminUsersOperationRemoverole(cls, WebRequest, Data, UserToEdit, CurrentUserAuth.User)

	# check all update values
	update:Dict[str, Any] = dict()

	# username
	Edit["username"] = Data.getStr("username", UNDEFINED, len_max=64)
	if Edit["username"] != UNDEFINED:
		update["username"] = Edit["username"]

	# email
	Edit["email"] = Data.getStr("email", UNDEFINED, len_max=128)
	if Edit["email"] != UNDEFINED:
		update["email"] = Edit["email"]

	# password
	Edit["password"] = Data.getStr("password", UNDEFINED, len_max=256)
	if Edit["password"]: # aka non empty string and not UNDEFINED
		Edit["password"] = passwordFunction(Edit["password"])
		update["password"] = Edit["password"]

	# verified
	Edit["verified"] = Data.getBool("verified", UNDEFINED)
	if Edit["verified"] != UNDEFINED:
		update["verified"] = Edit["verified"]

	if not update:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="No changes, please add at least one")

	cls.BASE.Logger.debug(f"(API) Config User U:{Edit['user_id']} {str(update)}", require="api:user")
	cls.BASE.PhaazeDB.updateQuery(
		table="user",
		content=update,
		where="`user`.`id` = %s",
		where_values=(Edit["user_id"],)
	)

	return cls.response(
		text=json.dumps(dict(msg="user successful updated", update=update, status=200)),
		content_type="application/json",
		status=200
	)

async def apiAdminUsersOperationAddrole(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, Data:WebRequestContent, EditUser:WebUser, CurrentUser:WebUser) -> Response:
	"""
	Default url: /api/admin/users/edit?operation=addrole
	"""
	# get required stuff
	role_id:int = Data.getInt("role_id", 0, min_x=1)

	# checks
	if not role_id:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'role_id'")

	res:List[WebRole] = await getWebRoles(cls, role_id=role_id)
	if not res:
		return await cls.Tree.Api.Admin.Roles.errors.apiAdminRoleNotExists(cls, WebRequest, role_id=role_id)

	WantedRole:WebRole = res.pop(0)

	if EditUser.checkRoles(WantedRole.name):
		return await cls.Tree.Api.errors.apiWrongData(cls, WebRequest, msg=f"{EditUser.username} already has role: {WantedRole.name}")

	if WantedRole.name.lower() in ["superadmin", "admin"]:
		if not (CurrentUser.checkRoles("superadmin")):
			return await cls.Tree.Api.errors.apiNotAllowed(cls, WebRequest, msg=f"Only Superadmin's can assign/remove {WantedRole.name} to user")

	cls.BASE.PhaazeDB.insertQuery(
		table="web_user+web_role",
		content={"user_id":EditUser.user_id, "role_id":WantedRole.role_id}
	)

	return cls.response(
		text=json.dumps(dict(msg="User: added role", add=WantedRole.name, status=200)),
		content_type="application/json",
		status=200
	)

async def apiAdminUsersOperationRemoverole(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, Data:WebRequestContent, EditUser:WebUser, CurrentUser:WebUser) -> Response:
	"""
	Default url: /api/admin/users/edit?operation=removerole
	"""
	# get required stuff
	role_id:int = Data.getInt("role_id", 0, min_x=1)

	# checks
	if not role_id:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'role_id'")

	res:List[WebRole] = await getWebRoles(cls, role_id=role_id)
	if not res:
		return await cls.Tree.Api.Admin.Roles.errors.apiAdminRoleNotExists(cls, WebRequest, role_id=role_id)

	UnwantedRole:WebRole = res.pop(0)

	if not EditUser.checkRoles(UnwantedRole.name):
		return await cls.Tree.Api.errors.apiWrongData(cls, WebRequest, msg=f"{EditUser.username} don't have role: {UnwantedRole.name}")

	if UnwantedRole.name.lower() in ["superadmin", "admin"]:
		if not (CurrentUser.checkRoles("superadmin")):
			return await cls.Tree.Api.errors.apiNotAllowed(cls, WebRequest, msg=f"Only Superadmin's can assign/remove {UnwantedRole.name} to user")

	cls.BASE.PhaazeDB.deleteQuery("""
		DELETE FROM `web_user+web_role`
		WHERE `user_id` = %s
			AND `role_id` = %s""",
		(EditUser.user_id, UnwantedRole.role_id)
	)

	return cls.response(
		text=json.dumps(dict(msg="User: removed role", remove=UnwantedRole.name, status=200)),
		content_type="application/json",
		status=200
	)
