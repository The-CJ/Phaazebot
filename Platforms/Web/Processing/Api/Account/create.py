from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

import json
import re
from aiohttp.web import Response
from Utils.Classes.authwebuser import AuthWebUser
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Web.db import getWebUsers
from Platforms.Web.utils import authWebUser
from Utils.regex import IsEmail
from Utils.stringutils import passwordToHash as passwordFunction

async def apiAccountCreatePhaaze(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
		Default url: /api/account/phaaze/create
	"""

	WebAuth:AuthWebUser = await authWebUser(cls, WebRequest)

	if WebAuth.found:
		return await cls.Tree.Api.Account.errors.apiAccountAlreadyLoggedIn(cls, WebRequest)

	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	username:str = Data.getStr("username", "", len_max=64)
	email:str = Data.getStr("email", "", len_max=128)
	password:str = Data.getStr("password", "", len_max=256)
	password2:str = Data.getStr("password2", "", len_max=256)

	# checks
	if password != password2:
		return await cls.Tree.Api.Account.errors.apiAccountPasswordsDontMatch(cls, WebRequest)

	if len(password) < 8:
		return await cls.Tree.Api.Account.errors.apiAccountPasswordToShort(cls, WebRequest, min_length=8)

	if not re.match(IsEmail, email):
		return await cls.Tree.Api.Account.errors.apiAccountEmailWrong(cls, WebRequest, email=email)

	res_users:list = await getWebUsers(cls, overwrite_where=" AND LOWER(`user`.`username`) = LOWER(%s) OR LOWER(`user`.`email`) = LOWER(%s)", overwrite_where_values=(username, email))
	if res_users:
		return await cls.Tree.Api.Account.errors.apiAccountTaken(cls, WebRequest, email=email, username=username)

	# everything ok -> create
	user_id:int = cls.BASE.PhaazeDB.insertQuery(
		table="user",
		content={
			"username": username,
			"password": passwordFunction(password),
			"email": email,
		}
	)

	cls.BASE.Logger.debug(f"(API) Account: Created {user_id=}", require="api:create")
	return cls.response(
		body=json.dumps(dict(status=200, message="successful created user", user_id=user_id, username=username)),
		content_type="application/json",
		status=200
	)
