from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
import re
from aiohttp.web import Response, Request
from Utils.Classes.webuserinfo import WebUserInfo
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Web.utils import getWebUsers
from Utils.regex import IsEmail
from Utils.stringutils import password as password_function
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

	WebUser:WebUserInfo = await cls.getWebUserInfo(WebRequest)

	if WebUser.found:
		return await apiAccountAlreadyLoggedIn(cls, WebRequest, user_id=WebUser.user_id)

	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	username:str = Data.getStr("username", "")
	email:str = Data.getStr("email", "")
	password:str = Data.getStr("password", "")
	password2:str = Data.getStr("password2", "")

	# checks
	if password != password2:
		return await apiAccountPasswordsDontMatch(cls, WebRequest)

	if len(password) < 8:
		return await apiAccountPasswordToShort(cls, WebRequest, min_length=8)

	if not re.match(IsEmail, email):
		return await apiAccountEmailWrong(cls, WebRequest, email=email)

	res_users:list = await getWebUsers(cls, "LOWER(`user`.`username`) = LOWER(%s) OR LOWER(`user`.`email`) = LOWER(%s)", (username, email))
	if res_users:
		return await apiAccountTaken(cls, WebRequest, email=email, username=username)

	# everything ok -> create
	new_user:dict = dict(
		username = username,
		password = password_function(password),
		email = email
	)

	user_id:int = cls.Web.BASE.PhaazeDB.insertQuery(
		table = "user",
		content = new_user
	)

	cls.Web.BASE.Logger.debug(f"(API) Account created: ID: {user_id}", require="api:create")
	return cls.response(
		body=json.dumps( dict(status=200, message="successfull created user", user_id=user_id, username=username) ),
		content_type="application/json",
		status=200
	)
