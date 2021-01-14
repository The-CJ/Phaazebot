from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request
from Utils.Classes.authwebuser import AuthWebUser
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.undefined import UNDEFINED
from Utils.stringutils import passwordToHash as password_function
from Platforms.Web.db import getWebUsers
from Platforms.Web.Processing.Api.errors import apiMissingData
from Platforms.Web.Processing.Api.Account.errors import apiAccountTaken

async def apiAdminUsersCreate(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/admin/users/create
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	username:str = Data.getStr("username", UNDEFINED, len_max=64)
	email:str = Data.getStr("email", UNDEFINED, len_max=128)
	password:str = Data.getStr("password", UNDEFINED, len_max=256)

	# checks
	if not username or not email or not password:
		return await apiMissingData(cls, WebRequest, msg="missing 'username', 'email' or 'password'")

	password = password_function(password)

	res_users:List[AuthWebUser] = await getWebUsers(cls,
	                                                where="LOWER(`user`.`username`) = LOWER(%s) OR LOWER(`user`.`email`) = LOWER(%s)",
	                                                where_values=(username, email)
	                                                )

	if res_users:
		return await apiAccountTaken(cls, WebRequest)

	new_id:int = cls.Web.BASE.PhaazeDB.insertQuery(
		table = "user",
		content = dict(
			username=username,
			email=email,
			password=password
		)
	)

	cls.Web.BASE.Logger.debug(f"(API/Admin) Created user '{username}' (ID:{new_id})", require="api:user")
	return cls.response(
		text=json.dumps( dict(msg="successfull created user", user_id=new_id, status=200) ),
		content_type="application/json",
		status=200
	)
