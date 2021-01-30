from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

import json
from aiohttp.web import Response
from Utils.Classes.webuser import WebUser
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.storagetransformer import StorageTransformer
from Utils.Classes.undefined import UNDEFINED
from Utils.stringutils import passwordToHash as passwordFunction
from Platforms.Web.db import getWebUsers

async def apiAdminUsersCreate(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/admin/users/create
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	Create:StorageTransformer = StorageTransformer()
	Create["username"] = Data.getStr("username", UNDEFINED, len_max=64)
	Create["email"] = Data.getStr("email", UNDEFINED, len_max=128)
	Create["password"] = Data.getStr("password", UNDEFINED, len_max=256)

	# checks
	if not Create["username"] or not Create["email"] or not Create["password"]:
		return await cls.Tree.Api.errors.apiMissingData(cls, WebRequest, msg="missing 'username', 'email' or 'password'")

	Create["password"] = passwordFunction(Create["password"])

	res_users:List[WebUser] = await getWebUsers(cls, overwrite_where=" AND LOWER(`user`.`username`) = LOWER(%s) OR LOWER(`user`.`email`) = LOWER(%s)", overwrite_where_values=(Create["username"], Create["email"]))

	if res_users:
		return await cls.Tree.Api.Account.errors.apiAccountTaken(cls, WebRequest)

	new_id:int = cls.BASE.PhaazeDB.insertQuery(
		table="user",
		content=Create.getAllTransform()
	)

	cls.BASE.Logger.debug(f"(API/Admin) Created user '{Create['username']}' (ID:{new_id})", require="api:user")
	return cls.response(
		text=json.dumps(dict(msg="successful created user", user_id=new_id, status=200)),
		content_type="application/json",
		status=200
	)
