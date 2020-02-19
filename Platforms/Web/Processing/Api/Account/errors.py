from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request

async def apiAccountAlreadyLoggedIn(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
			user_id:str
			user_name:str
	"""
	res:dict = dict(status=400, error="aleady_logged_in")

	user_id:str = kwargs.get("user_id", "")
	if user_id:
		res["user_id"] = user_id

	user_name:str = kwargs.get("user_name", "")
	if user_name:
		res["user_name"] = user_name

	# build message
	default_msg:str = "No registration needed, already logged in"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.Web.BASE.Logger.debug(f"(API) Account create already exists - User ID: {user_id}", require="api:create")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)

async def apiAccountPasswordsDontMatch(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
	"""
	res:dict = dict(status=400, error="unequal_passwords")

	# build message
	default_msg:str = "The passwords are not the same"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.Web.BASE.Logger.debug(f"(API) Account create failed, passwords don't match", require="api:create")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)

async def apiAccountPasswordToShort(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
			min_length:int
	"""
	res:dict = dict(status=400, error="invalid_password")

	min_length:str = kwargs.get("min_length", 0)
	if min_length:
		res["min_length"] = min_length

	# build message
	default_msg:str = f"The password is to short"

	if min_length:
		default_msg += f", it must be at least {min_length} chars long"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.Web.BASE.Logger.debug(f"(API) Account create failed, password to short", require="api:create")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)

async def apiAccountEmailWrong(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
			email:str
	"""
	res:dict = dict(status=400, error="invalid_email")

	email:str = kwargs.get("email", "")
	if email:
		res["email"] = email

	# build message
	default_msg:str = f"E-Mail doesn't look valid"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.Web.BASE.Logger.debug(f"(API) Account create failed, email looks false: {email}", require="api:create")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)

async def apiAccountTaken(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
			email:str
			username:str
	"""
	res:dict = dict(status=400, error="account_taken")

	username:str = kwargs.get("username", "")
	if username:
		res["username"] = username

	email:str = kwargs.get("email", "")
	if email:
		res["email"] = email

	# build message
	default_msg:str = f"Username or E-Mail is already taken"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.Web.BASE.Logger.debug(f"(API) Account create failed, account already taken: {username} - {email}", require="api:create")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)
