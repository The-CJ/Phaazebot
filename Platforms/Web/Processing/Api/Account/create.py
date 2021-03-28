from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

import json
import re
from aiohttp.web import Response
from Utils.Classes.authwebuser import AuthWebUser
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.storagetransformer import StorageTransformer
from Platforms.Web.utils import authWebUser
from Platforms.Web.db import getWebUsers
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
	Create:StorageTransformer = StorageTransformer()
	Create["username"] = Data.getStr("username", "", len_max=64)
	Create["email"] = Data.getStr("email", "", len_max=128)
	Create["password"] = Data.getStr("password", "", len_max=256)
	Create["password2"] = Data.getStr("password2", "", len_max=256)

	# checks
	if Create["password"] != Create["password2"]:
		return await cls.Tree.Api.Account.errors.apiAccountPasswordsDontMatch(cls, WebRequest)

	if len(Create["password"]) < 8:
		return await cls.Tree.Api.Account.errors.apiAccountPasswordToShort(cls, WebRequest, min_length=8)

	if not re.match(IsEmail, Create["email"]):
		return await cls.Tree.Api.Account.errors.apiAccountEmailWrong(cls, WebRequest, email=Create["email"])

	res_users:list = await getWebUsers(cls, overwrite_where=" AND LOWER(`user`.`username`) = LOWER(%s) OR LOWER(`user`.`email`) = LOWER(%s)", overwrite_where_values=(Create["username"], Create["email"]))
	if res_users:
		return await cls.Tree.Api.Account.errors.apiAccountTaken(cls, WebRequest, email=Create["email"], username=Create["username"])

	# everything ok -> create
	user_id:int = cls.BASE.PhaazeDB.insertQuery(
		table="user",
		content={
			"username": Create["username"],
			"password": passwordFunction(Create["password"]),
			"email": Create["email"],
		}
	)

	cls.BASE.Logger.debug(f"(API) Account: Created {user_id=}", require="api:create")
	return cls.response(
		body=json.dumps(dict(status=200, message="successful created user", user_id=user_id, username=Create["username"])),
		content_type="application/json",
		status=200
	)
