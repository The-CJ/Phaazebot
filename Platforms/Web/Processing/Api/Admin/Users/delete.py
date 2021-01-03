from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.authwebuser import AuthWebUser
from Platforms.Web.db import getWebUsers
from Platforms.Web.Processing.Api.errors import (
	apiMissingData,
	apiNotAllowed,
	apiUserNotFound
)

async def apiAdminUsersDelete(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/admin/users/delete
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	user_id:int = Data.getInt("user_id", 0, min_x=1)

	# checks
	if not user_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'user_id'")

	# get user
	res_users:List[AuthWebUser] = await getWebUsers(cls, user_id=user_id)
	if not res_users:
		return await apiUserNotFound(cls, WebRequest, user_id=user_id)
	UserToDelete:AuthWebUser = res_users.pop(0)

	# check for higher users
	if UserToDelete.checkRoles(["superadmin", "admin"]):
		if not ( await cls.getWebUserInfo(WebRequest) ).checkRoles(["superadmin"]):
			return await apiNotAllowed(cls, WebRequest, msg=f"Only Superadmin's can delete (Super)admin user")

	cls.Web.BASE.PhaazeDB.deleteQuery("""
	 	DELETE FROM `user`
		WHERE `user`.`id` = %s LIMIT 1""",
		(UserToDelete.user_id,)
	)

	cls.Web.BASE.Logger.debug(f"(API) Deleted user {user_id=}", require="api:user")

	return cls.response(
		text=json.dumps( dict(msg="user successfull deleted", status=200) ),
		content_type="application/json",
		status=200
	)
