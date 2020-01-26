from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.webuserinfo import WebUserInfo
from Platforms.Web.utils import getWebUsers
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
	user_id:str = Data.getStr("user_id", "", must_be_digit=True)

	# checks
	if not user_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'user_id'")

	# format
	where:str = f"`user`.`id` = {user_id}"

	# get user
	res_users:list = await getWebUsers(cls, where=where)
	if not res_users:
		return await apiUserNotFound(cls, WebRequest, msg=f"no user found with id: {user_id}")
	UserToDelete:WebUserInfo = res_users.pop(0)

	# check for higher users
	if UserToDelete.checkRoles(["superadmin", "admin"]):
		if not ( await cls.getWebUserInfo(WebRequest) ).checkRoles(["superadmin"]):
			return await apiNotAllowed(cls, WebRequest, msg=f"Only Superadmin's can delete (Super)admin user")

	cls.Web.BASE.PhaazeDB.deleteQuery("""
	 	DELETE FROM `user`
		WHERE `user`.`id` = %s LIMIT 1""",
		(UserToDelete.user_id,)
	)

	cls.Web.BASE.Logger.debug(f"(API) Deleted user U:{user_id}", require="api:user")

	return cls.response(
		text=json.dumps( dict(msg="user successfull deleted", status=200) ),
		content_type="application/json",
		status=200
	)
