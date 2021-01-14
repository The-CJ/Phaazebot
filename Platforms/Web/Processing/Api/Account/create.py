from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
import re
from aiohttp.web import Response, Request
from Utils.Classes.authwebuser import AuthWebUser
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Web.db import getWebUsers
from Utils.regex import IsEmail
from Utils.stringutils import passwordToHash as password_function
from Platforms.Web.Processing.Api.Account.errors import (
	apiAccountAlreadyLoggedIn,
	apiAccountPasswordsDontMatch,
	apiAccountPasswordToShort,
	apiAccountEmailWrong,
	apiAccountTaken
)

async def apiAccountCreatePhaaze(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/phaaze/create
	"""

	WebUser:AuthWebUser = await cls.getWebUserInfo(WebRequest)

	if WebUser.found:
		return await apiAccountAlreadyLoggedIn(cls, WebRequest, user_id=WebUser.user_id)

	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	username:str = Data.getStr("username", "", len_max=64)
	email:str = Data.getStr("email", "", len_max=128)
	password:str = Data.getStr("password", "", len_max=256)
	password2:str = Data.getStr("password2", "", len_max=256)

	# checks
	if password != password2:
		return await apiAccountPasswordsDontMatch(cls, WebRequest)

	if len(password) < 8:
		return await apiAccountPasswordToShort(cls, WebRequest, min_length=8)

	if not re.match(IsEmail, email):
		return await apiAccountEmailWrong(cls, WebRequest, email=email)

	res_users:list = await getWebUsers( cls, where="LOWER(`user`.`username`) = LOWER(%s) OR LOWER(`user`.`email`) = LOWER(%s)",	where_values=(username, email) )
	if res_users:
		return await apiAccountTaken(cls, WebRequest, email=email, username=username)

	# everything ok -> create
	user_id:int = cls.Web.BASE.PhaazeDB.insertQuery(
		table = "user",
		content = {
			"username": username,
			"password": password_function(password),
			"email": email,
		}
	)

	cls.Web.BASE.Logger.debug(f"(API) Account: Created {user_id=}", require="api:create")
	return cls.response(
		body=json.dumps( dict(status=200, message="successfull created user", user_id=user_id, username=username) ),
		content_type="application/json",
		status=200
	)
