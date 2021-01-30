from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

import json
from aiohttp.web import Response
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.webuser import WebUser
from Platforms.Web.utils import authWebUser
from Platforms.Web.db import getWebUsers

async def apiAdminUsersDelete(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/admin/users/delete
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	user_id:int = Data.getInt("user_id", 0, min_x=1)

	# checks
	if not user_id:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing or invalid 'user_id'")

	# get user
	res_users:List[WebUser] = await getWebUsers(cls, user_id=user_id)
	if not res_users:
		return await cls.Tree.Api.errors.apiUserNotFound(cls, WebRequest, user_id=user_id)
	UserToDelete:WebUser = res_users.pop(0)

	# check for higher users
	if UserToDelete.checkRoles(["superadmin", "admin"]):
		if not (await authWebUser(cls,WebRequest)).User.checkRoles(["superadmin"]):
			return await cls.Tree.Api.errors.apiNotAllowed(cls, WebRequest, msg=f"Only Superadmin's can delete (Super)admin user")

	cls.BASE.PhaazeDB.deleteQuery("""
		DELETE FROM `user`
		WHERE `user`.`id` = %s LIMIT 1""",
		(UserToDelete.user_id,)
	)

	cls.BASE.Logger.debug(f"(API) Deleted user {user_id=}", require="api:user")

	return cls.response(
		text=json.dumps(dict(msg="user successful deleted", status=200)),
		content_type="application/json",
		status=200
	)
