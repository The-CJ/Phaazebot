from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
import re
import datetime
from aiohttp.web import Response, Request
from Utils.Classes.webuserinfo import WebUserInfo
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.stringutils import password as password_function
from Utils.regex import IsEmail
from Platforms.Web.utils import getWebUsers
from Platforms.Web.Processing.Api.errors import apiWrongData, apiMissingAuthorisation
from Platforms.Web.Processing.Api.Account.errors import (
	apiAccountPasswordsDontMatch,
	apiAccountPasswordToShort,
	apiAccountTaken,
	apiAccountEmailWrong
)

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
	current_password:str = Data.getStr("password", "")
	new_username:str = Data.getStr("username", "")
	new_email:str = Data.getStr("email", "")
	new_password:str = Data.getStr("newpassword", "")
	new_password2:str = Data.getStr("newpassword2", "")

	# checks
	if not current_password or WebUser.password != password_function(current_password):
		return await apiAccountPasswordsDontMatch(cls, WebRequest, msg="Current password is not correct")

	changed_email:bool = False # if yes, reset valiated and send mail

	update:dict = dict()

	# if new_password is set, check all and set to update
	if new_password:
		if new_password != new_password2:
			return await apiAccountPasswordsDontMatch(cls, WebRequest)

		if len(new_password) < 8:
			return await apiAccountPasswordToShort(cls, WebRequest, min_length=8)

		update["password"] = password_function(new_password)

	if new_username:
		# want a new username
		if new_username.lower() != WebUser.username.lower():
			is_occupied:list = await getWebUsers(cls, "LOWER(`user`.`username`) = LOWER(%s)", (new_username,))
			if is_occupied:
				# already taken
				return await apiAccountTaken(cls, WebRequest)

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
			return await apiAccountEmailWrong(cls, WebRequest, email=new_email)

		is_occupied:list = await getWebUsers(cls, "user.email LIKE %s", (new_email,))
		if is_occupied:
			# already taken
			return await apiAccountTaken(cls, WebRequest)

		else:
			changed_email = True
			update["email"] = new_email

	if not update:
		return await apiWrongData(cls, WebRequest, msg=f"No changes, please add at least one")

	# verification mail
	if changed_email:
		cls.Web.BASE.Logger.warning(f"(API) New Email, send new verification mail: {new_email}", require="api:account")
		# TODO: SEND MAIL

	update["edited_at"] = str(datetime.datetime.now())

	cls.Web.BASE.PhaazeDB.updateQuery(
		table = "user",
		content = update,
		where = "`user`.`id` = %s",
		where_values = (WebUser.user_id,)
	)
	
	cls.Web.BASE.Logger.debug(f"(API) Account edit ({WebUser.user_id}) : {str(update)}", require="api:account")
	return cls.response(
		status=200,
		text=json.dumps( dict(error="successfull_edited", msg="Your account has been successfull edited", update=update, status=200) ),
		content_type="application/json"
	)
