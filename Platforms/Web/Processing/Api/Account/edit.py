from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
import re
import traceback
import datetime
from ..errors import apiMissingAuthorisation
from aiohttp.web import Response, Request
from Utils.Classes.webuserinfo import WebUserInfo
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.stringutils import password as password_function
from Utils.regex import IsEmail
from Platforms.Web.utils import getWebUsers
from Platforms.Web.Processing.Api.errors import apiWrongData

async def apiAccountEditPhaaze(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/phaaze/edit
	"""
	WebUser:WebUserInfo = await cls.getWebUserInfo(WebRequest)

	if not WebUser.found:
		return await apiMissingAuthorisation(cls, WebRequest)

	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	current_password:str = Data.getStr("phaaze_password", "")
	new_username:str = Data.getStr("phaaze_username", "")
	new_email:str = Data.getStr("phaaze_email", "")
	new_password:str = Data.getStr("phaaze_newpassword", "")
	new_password2:str = Data.getStr("phaaze_newpassword2", "")

	# checks
	if not current_password or WebUser.password != password_function(current_password):
		return cls.response(
			status=400,
			text=json.dumps( dict(error="current_password_wrong", msg="Current password is not correct", status=400) ),
			content_type="application/json"
		)

	changed_email:bool = False # if yes, reset valiated and send mail

	update:dict = dict()

	# if new_password is set, check all and set to update
	if new_password:
		if new_password != new_password2:
			cls.Web.BASE.Logger.debug(f"(API) Account edit failed, passwords don't match", require="api:create")
			return cls.response(
				text=json.dumps( dict(error="unequal_passwords", status=400, msg="the passwords are not the same") ),
				content_type="application/json",
				status=400
			)

		if len(new_password) < 7:
			cls.Web.BASE.Logger.debug(f"(API) Account edit failed, password to short", require="api:create")
			return cls.response(
				body=json.dumps( dict(error="invalid_password", status=400, msg="the password must be at least 8 chars long") ),
				content_type="application/json",
				status=400
			)

		update["password"] = password_function(new_password)

	if new_username:
		# want a new username
		if new_username.lower() != WebUser.username.lower():
			is_occupied:list = await getWebUsers(cls, "LOWER(`user`.`username`) = LOWER(%s)", (new_username,))
			if is_occupied:
				# already taken
				return cls.response(
					status=400,
					text=json.dumps( dict(error="account_taken", msg="username or email is taken", status=400) ),
					content_type="application/json"
				)
			else:
				# username is free, add to update and add one to username_changed,
				# maybe i do something later with it
				update["username_changed"] = WebUser.username_changed + 1
				update["username"] = new_username

		# else, it's a diffrent captation or so
		elif new_username != WebUser.username:
			update["username"] = new_username

	if new_email and new_email.lower() != WebUser.email:
		if re.match(IsEmail, new_email) == None:
			# does not look like a email
			return cls.response(
				text=json.dumps( dict(error="invalid_email", status=400, msg="email looks false") ),
				content_type="application/json",
				status=400
			)
		is_occupied:list = await getWebUsers(cls, "user.email LIKE %s", (new_email,))
		if is_occupied:
			# already taken
			return cls.response(
				status=400,
				text=json.dumps( dict(error="account_taken", msg="username or email is taken", status=400) ),
				content_type="application/json"
			)
		else:
			changed_email = True
			update["email"] = new_email

	if not update:
		return await apiWrongData(cls, WebRequest, msg=f"No changes, please add at least one")

	# verification mail
	if changed_email:
		cls.Web.BASE.Logger.debug(f"(API) New Email, send new verification mail: {new_email}", require="api:account")
		# TODO: SEND MAIL

	update["edited_at"] = str(datetime.datetime.now())

	try:
		cls.Web.BASE.PhaazeDB.updateQuery(
			table = "user",
			content = update,
			where = "user.id = %s",
			where_values = (WebUser.user_id,)
		)
		cls.Web.BASE.Logger.debug(f"(API) Account edit ({WebUser.user_id}) : {str(update)}", require="api:account")
		return cls.response(
			status=200,
			text=json.dumps( dict(error="successfull_edited", msg="Your account has been successfull edited", changes=update, status=200) ),
			content_type="application/json"
		)

	except Exception as e:
		tb:str = traceback.format_exc()
		cls.Web.BASE.Logger.error(f"(API) Account edit failed ({WebUser.user_id}) - {str(e)}\n{tb}")
		return cls.response(
			status=500,
			text=json.dumps( dict(error="edit_failed", msg="Editing you account failed", status=500) ),
			content_type="application/json"
		)
