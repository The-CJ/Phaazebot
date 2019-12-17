from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.undefined import UNDEFINED
from Utils.stringutils import password as password_function
from Platforms.Web.Processing.Api.errors import apiMissingData

async def apiAdminUsersCreate(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/admin/users/create
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	username:str = Data.getStr("username", UNDEFINED)
	email:str = Data.getStr("email", UNDEFINED)
	password:str = Data.getStr("password", UNDEFINED)

	# format
	if password:
		password = password_function(password)

	# checks
	if not username or not email or not password:
		return await apiMissingData(cls, WebRequest, msg="missing 'username', 'email' or 'password'")

	try:
		new_id:int = cls.Web.BASE.PhaazeDB.insertQuery(
			table = "user",
			content = dict(
				username=username,
				email=email,
				password=password
			)
		)

		cls.Web.BASE.Logger.debug(f"(API) Create user '{username}' (ID:{new_id})", require="api:user")
		return cls.response(
			text=json.dumps( dict(msg="user successfull created", status=200) ),
			content_type="application/json",
			status=200
		)

	except:
		cls.Web.BASE.Logger.debug(f"(API) Create user failed, account already taken: {str(username)} - {str(email)}", require="api:create")
		return cls.response(
			body=json.dumps( dict(error="account_taken", status=400, msg="username or email is already taken") ),
			content_type="application/json",
			status=400
		)
