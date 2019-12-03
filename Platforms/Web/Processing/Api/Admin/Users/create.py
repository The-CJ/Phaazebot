from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.webrole import WebRole
from Platforms.Web.Processing.Api.errors import missingData
from Utils.Classes.undefined import UNDEFINED
from Utils.dbutils import validateDBInput
from Utils.stringutils import password as password_function

async def apiAdminUsersCreate(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/admin/users/create
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# username
	username:str = Data.getStr("username", "")

	# email
	email:str = Data.getStr("email", "")

	# password
	password:str = Data.getStr("password", "")
	if password: password = password_function(password)

	if not username or not email or not password:
		return await missingData(cls, WebRequest, msg="missing 'username', 'email' or 'password'")

	try:
		new_id:int = cls.Web.BASE.PhaazeDB.insertQuery(
			table = "user",
			content = dict(username=username, email=email, password=password)
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
