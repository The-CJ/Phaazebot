from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
import re
import datetime
import traceback
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

	username:str = Data.getStr("username", "")
	email:str = Data.getStr("email", "")
	password:str = Data.getStr("password", "")
	password2:str = Data.getStr("password2", "")

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

	check:list = await searchUser(cls, "user.username LIKE %s OR user.email LIKE %s", (username, email))
	if check:
		cls.Web.BASE.Logger.debug(f"(API) Account create failed, account already taken: {str(username)} - {str(email)}", require="api:create")
		return cls.response(
			body=json.dumps( dict(error="account_taken", status=400, msg="username or email is already taken") ),
			content_type="application/json",
			status=400
		)

	# everything ok -> create
	try:
		cls.Web.BASE.PhaazeDB.query("""
			INSERT INTO user
			(username, password, email)
			VALUES (%s, %s, %s)""", (username, password_function(password), email)
		)

		res:list = cls.Web.BASE.PhaazeDB.query("""SELECT id FROM user WHERE username LIKE %s""", (username,))
		if not res: raise

		user_id:str = res[0]["id"]
		cls.Web.BASE.Logger.debug(f"(API) Account created: ID: {user_id}", require="api:create")
		return cls.response(
			body=json.dumps( dict(status=200, message="successfull created user", id=user_id, username=username) ),
			content_type="application/json",
			status=200
		)
	except Exception as e:
		tb:str = traceback.format_exc()
		cls.Web.BASE.Logger.error(f"(API) Database error: {str(e)}\n{tb}")
		return cls.response(
			body=json.dumps( dict(status=400, msg="create user failed") ),
			content_type="application/json",
			status=400
		)
