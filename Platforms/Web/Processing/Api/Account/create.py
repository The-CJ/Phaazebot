from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
import re
from aiohttp.web import Response, Request
from Utils.Classes.webuserinfo import WebUserInfo
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Web.utils import searchUser
from Utils.regex import IsEmail
from Utils.stringutils import password as password_function

async def apiAccountCreatePhaaze(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/phaaze/create
	"""

	UserInfo:WebUserInfo = await cls.getUserInfo(WebRequest)

	if UserInfo.found:
		cls.Web.BASE.Logger.debug(f"(API) Account create already exists - User ID: {UserInfo.user_id}", require="api:create")
		return cls.response(
			body=json.dumps( dict(error="aleady_logged_in", status=400, msg="no registion needed, already logged in") ),
			content_type="application/json",
			status=400
		)

	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	username:str = Data.get("username")
	email:str = Data.get("email")
	password:str = Data.get("password")
	password2:str = Data.get("password2")

	if password != password2:
		cls.Web.BASE.Logger.debug(f"(API) Account create failed, passwords don't match", require="api:create")
		return cls.response(
			body=json.dumps( dict(error="unequal_passwords", status=400, msg="the passwords are not the same") ),
			content_type="application/json",
			status=400
		)

	if len(password) < 7:
		cls.Web.BASE.Logger.debug(f"(API) Account create failed, password to short", require="api:create")
		return cls.response(
			body=json.dumps( dict(error="invalid_password", status=400, msg="the password must be at least 8 chars long") ),
			content_type="application/json",
			status=400
		)

	if not re.match(IsEmail, email):
		cls.Web.BASE.Logger.debug(f"(API) Account create failed, email looks false: {str(email)}", require="api:create")
		return cls.response(
			body=json.dumps( dict(error="invalid_email", status=400, msg="email looks false") ),
			content_type="application/json",
			status=400
		)

	check:list = await searchUser(cls, f"user['username'].lower() == {json.dumps(username)}.lower() or user['email'].lower() == {json.dumps(email)}.lower()")
	if check:
		cls.Web.BASE.Logger.debug(f"(API) Account create failed, account already taken: {str(username)} - {str(email)}", require="api:create")
		return cls.response(
			body=json.dumps( dict(error="account_taken", status=400, msg="username or email is already taken") ),
			content_type="application/json",
			status=400
		)

	# everything ok, create

	new_user:dict = dict(
		username= username,
		password = password_function(password),
		email = email,
	)

	#TODO: need to send email verification

	cls.Web.BASE.Logger.debug(f"(API) Account created: {str(new_user)}", require="api:create")
	return cls.response(
		text=json.dumps( dict(debug=Data.content,status=200) ),
		content_type="application/json",
		status=400
	)
