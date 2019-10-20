from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request

async def apiUnknown(cls:"WebIndex", WebRequest:Request, **kwargs:Any) -> Response:
	"""
		Takes from kwargs: None
	"""
	cls.Web.BASE.Logger.debug(f"(API) 404: {WebRequest.path}", require="api:404")
	return cls.response(
		text=json.dumps( dict(error="unknown_api", status=404) ),
		content_type="application/json",
		status=404
	)

async def apiNothing(cls:"WebIndex", WebRequest:Request, **kwargs:Any) -> Response:
	"""
		Takes from kwargs:
			msg:str
	"""
	default_msg:str = f"Trying to find out the PhaazeAPI?. Try looking at {cls.Web.BASE.Vars.WEB_ROOT}/wiki/api"
	msg:str = kwargs.get("msg", default_msg)

	cls.Web.BASE.Logger.debug(f"(API) 400: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( dict(error="no_path", status=400, msg=msg) ),
		content_type="application/json",
		status=400
	)

async def apiNotAllowed(cls:"WebIndex", WebRequest:Request, **kwargs:Any) -> Response:
	"""
		Takes from kwargs:
			msg:str
	"""
	default_msg:str = "Not allowed"
	msg:str = kwargs.get("msg", default_msg)

	cls.Web.BASE.Logger.debug(f"(API) 403: {WebRequest.path}", require="api:403")
	return cls.response(
		text=json.dumps( dict(error="action_not_allowed", status=403, msg=msg) ),
		content_type="application/json",
		status=403
	)

async def apiMissingValidMethod(cls:"WebIndex", WebRequest:Request, **kwargs:Any) -> Response:
	"""
		Takes from kwargs:
			msg:str
	"""
	default_msg:str = "Missing valid method"
	msg:str = kwargs.get("msg", default_msg)

	cls.Web.BASE.Logger.debug(f"(API) 400: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( dict(error="missing_valid_method", status=400, msg=msg) ),
		content_type="application/json",
		status=400
	)

async def apiMissingAuthorisation(cls:"WebIndex", WebRequest:Request, **kwargs:Any) -> Response:
	"""
		Takes from kwargs: None
	"""

	cls.Web.BASE.Logger.debug(f"(Web/API) Missing Authorisation", require="api:400")
	return cls.response(
		status=401,
		text=json.dumps( dict(error="missing_authorisation", status=401) ),
		content_type="application/json"
	)

async def apiWrongData(cls:"WebIndex", WebRequest:Request, **kwargs:Any) -> Response:
	"""
		Takes from kwargs:
			msg:str
	"""
	default_msg:str = "Wrong data passed"
	msg:str = kwargs.get("msg", default_msg)

	return cls.response(
		status=400,
		text=json.dumps( dict(error="wrong_data", msg=msg, status=400) ),
		content_type="application/json"
	)

async def userNotFound(cls:"WebIndex", WebRequest:Request, **kwargs:Any) -> Response:
	"""
		Takes from kwargs:
			msg:str
	"""
	default_msg:str = "No user could be found, check password or username"
	msg:str = kwargs.get("msg", default_msg)

	cls.Web.BASE.Logger.debug(f"(Web/API) User not found", require="api:400")
	return cls.response(
		text=json.dumps( dict(error="no_user_found", status=404, msg=msg) ),
		content_type="application/json",
		status=404
	)

async def missingData(cls:"WebIndex", WebRequest:Request, **kwargs:Any) -> Response:
	"""
		Takes from kwargs:
			msg:str
	"""
	default_msg:str = "Missing required data"
	msg:str = kwargs.get("msg", default_msg)

	cls.Web.BASE.Logger.debug(f"(Web/API) Missing Data for api request", require="api:400")
	return cls.response(
		text=json.dumps( dict(error="missing_data", status=400, msg=msg) ),
		content_type="application/json",
		status=400
	)
