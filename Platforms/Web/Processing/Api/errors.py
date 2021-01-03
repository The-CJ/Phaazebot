from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

import json
from aiohttp.web import Response
from Utils.Classes.extendedrequest import ExtendedRequest

async def apiUnknown(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	None

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	None
	"""
	res:dict = dict(status=404, error="unknown_api")

	cls.BASE.Logger.debug(f"(API) 404: {WebRequest.path}", require="api:404")
	return cls.response(
		text=json.dumps(res),
		content_type="application/json",
		status=404
	)

async def apiNothing(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	Trying to find out the PhaazeAPI?. Try looking at web_root/wiki/api
	"""
	res:dict = dict(status=400, error="no_path")

	# build message
	default_msg:str = f"Trying to find out the PhaazeAPI?. Try looking at {cls.BASE.Vars.web_root}/wiki/api"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.BASE.Logger.debug(f"(API) 400: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)

async def apiNotAllowed(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	Not allowed
	"""
	res:dict = dict(status=403, error="action_not_allowed")

	# build message
	default_msg:str = "Not allowed"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.BASE.Logger.debug(f"(API) 403: {WebRequest.path}", require="api:403")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=403
	)

async def apiMissingValidMethod(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	Missing valid api method
	"""
	res:dict = dict(status=400, error="missing_valid_method")

	# build message
	default_msg:str = "Missing valid api method"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.BASE.Logger.debug(f"(API) 400: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)

async def apiMissingAuthorisation(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	None

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	None
	"""
	res:dict = dict(status=401, error="missing_authorisation")

	cls.BASE.Logger.debug(f"(Web/API) Missing Authorisation", require="api:400")
	return cls.response(
		status=401,
		text=json.dumps( res ),
		content_type="application/json"
	)

async def apiWrongData(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	Wrong data passed
	"""
	res:dict = dict(status=400, error="wrong_data")

	# build message
	default_msg:str = "Wrong data passed"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	return cls.response(
		status=400,
		text=json.dumps( res ),
		content_type="application/json"
	)

async def apiNotFound(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	No data found
	"""
	res:dict = dict(status=400, error="not_found")

	default_msg:str = "No data found"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	return cls.response(
		status=400,
		text=json.dumps( res ),
		content_type="application/json"
	)

async def apiUserNotFound(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* user_id `str` *
	* username `str` *
	* password `str`

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	No user could be found
	"""
	res:dict = dict(status=404, error="no_user_found")

	username:str = kwargs.get("username", "")
	if username:
		res["username"] = username

	user_id:str = kwargs.get("user_id", "")
	if user_id:
		res["user_id"] = user_id

	password:str = kwargs.get("password", "")
	if password:
		# S0m3th1ngC00L -> S0m**********
		res["password"] = password[:3] + ("*" * len(password[3:]))

	# build message
	default_msg:str = "No user could be found"

	if username:
		default_msg += f" with username '{username}'"

	if user_id:
		default_msg += f" (User ID: {user_id})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.BASE.Logger.debug(f"(Web/API) User not found", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=404
	)

async def apiMissingData(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	Missing required data
	"""
	res:dict = dict(status=400, error="missing_data")

	# build message
	default_msg:str = "Missing required data"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.BASE.Logger.debug(f"(Web/API) Missing Data for api request", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)

async def apiTimeout(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* time `int` *

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	An timeout occurred during the request
	"""
	res:dict = dict(status=400, error="timeout_occurred")

	time:str = kwargs.get("time", None)
	if time:
		res["time"] = time

	# build message
	default_msg:str = "An timeout occurred during the request"

	if time:
		default_msg += f": [{time=}s]"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.BASE.Logger.debug(f"(Web/API) Timeout Request", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)
