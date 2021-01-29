from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

import json
import re
import datetime
from aiohttp.web import Response
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.authwebuser import AuthWebUser
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.storagetransformer import StorageTransformer
from Utils.Classes.undefined import UNDEFINED
from Utils.stringutils import passwordToHash as passwordFunction
from Utils.regex import IsEmail
from Platforms.Web.db import getWebUsers
from Platforms.Web.utils import authWebUser

async def apiAccountEditPhaaze(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/account/phaaze/edit
	"""
	WebAuth:AuthWebUser = await authWebUser(cls, WebRequest)

	if not WebAuth.found:
		return await cls.Tree.Api.errors.apiMissingAuthorisation(cls, WebRequest)

	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	Edit:StorageTransformer = StorageTransformer()
	Edit["current_password"] = Data.getStr("password", UNDEFINED, len_max=256)
	Edit["new_username"] = Data.getStr("username", UNDEFINED, len_max=64)
	Edit["new_email"] = Data.getStr("email", UNDEFINED, len_max=128)
	Edit["new_password"] = Data.getStr("newpassword", UNDEFINED, len_max=256)
	Edit["new_password2"] = Data.getStr("newpassword2", UNDEFINED, len_max=256)

	# checks
	if not Edit["current_password"] or WebAuth.User.password != passwordFunction(Edit["current_password"]):
		return await cls.Tree.Api.Account.errors.apiAccountPasswordsDontMatch(cls, WebRequest, msg="Current password is not correct")

	changed_email:bool = False # if yes, reset validate and send mail

	update:dict = dict()

	# if new_password is set, check all and set to update
	if Edit["new_password"]:
		if Edit["new_password"] != Edit["new_password2"]:
			return await cls.Tree.Api.Account.errors.apiAccountPasswordsDontMatch(cls, WebRequest)

		if len(Edit["new_password"]) < 8:
			return await cls.Tree.Api.Account.errors.apiAccountPasswordToShort(cls, WebRequest, min_length=8)

		update["password"] = passwordFunction(Edit["new_password"])

	if Edit["new_password"]:
		# want a new username
		if Edit["new_password"].lower() != WebAuth.User.username.lower():
			is_occupied:list = await getWebUsers(cls, overwrite_where=" AND LOWER(`user`.`username`) = LOWER(%s)", overwrite_where_values=(new_username,))
			if is_occupied:
				# already taken
				return await cls.Tree.Api.Account.errors.apiAccountTaken(cls, WebRequest)

			else:
				# username is free, add to update and add one to username_changed,
				# maybe i do something later with it
				update["username_changed"] = WebAuth.User.username_changed + 1
				update["username"] = Edit["new_username"]

		# else, it's a different capitation or so
		elif Edit["new_username"] != WebAuth.User.username:
			update["username"] = Edit["new_username"]

	if Edit["new_email"] and Edit["new_email"].lower() != WebAuth.User.email:
		if re.match(IsEmail, Edit["new_email"]) is None:
			# does not look like a email
			return await cls.Tree.Api.Account.errors.apiAccountEmailWrong(cls, WebRequest, email=Edit["new_email"])

		is_occupied:list = await getWebUsers(cls, email_contains=Edit["new_email"])
		if is_occupied:
			# already taken
			return await cls.Tree.Api.Account.errors.apiAccountTaken(cls, WebRequest)

		else:
			changed_email = True
			update["email"] = Edit["new_email"]

	if not update:
		return await cls.Tree.Api.errors.apiWrongData(cls, WebRequest, msg=f"No changes, please add at least one")

	# verification mail
	if changed_email:
		cls.BASE.Logger.warning(f"(API) New Email, send new verification mail: {Edit['new_email']}")
		# TODO: SEND MAIL

	update["edited_at"] = str(datetime.datetime.now())

	cls.BASE.PhaazeDB.updateQuery(
		table="user",
		content=update,
		where="`user`.`id` = %s",
		where_values=(WebAuth.User.user_id,)
	)

	cls.BASE.Logger.debug(f"(API) Account edit ({WebAuth.User.user_id}) : {str(update)}", require="api:account")
	return cls.response(
		status=200,
		text=json.dumps(dict(error="successful_edited", msg="Your account has been successful edited", update=update, status=200)),
		content_type="application/json"
	)
