from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request

async def apiDiscordExceptionRoleExists(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
			role_id:str
			role_name:str
	"""
	res:dict = dict(status=400, error="discord_exceptionrole_exists")

	role_id:str = kwargs.get("role_id", "")
	if role_id:
		res["role_id"] = str(role_id)

	role_name:str = kwargs.get("role_name", "")
	if role_name:
		res["role_name"] = str(role_name)

	# build message
	default_msg:str = "Exceptionrole already exists"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	if role_name:
		default_msg += f" for '{role_name}'"

	if role_id:
		default_msg += f" (Role ID:{role_id})"

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Role exists: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)

async def apiDiscordExceptionRoleNotExists(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
			exceptionrole_id:str
			role_id:str
	"""
	res:dict = dict(status=400, error="discord_exceptionrole_not_exists")

	exceptionrole_id:str = kwargs.get("exceptionrole_id", "")
	if exceptionrole_id:
		res["exceptionrole_id"] = str(exceptionrole_id)

	role_id:str = kwargs.get("role_id", "")
	if role_id:
		res["role_id"] = str(role_id)

	# build message
	default_msg:str = "No exceptionrole found"

	if role_id:
		default_msg += f" (Role ID:{role_id})"

	if exceptionrole_id:
		default_msg += f" (Exceptionrole ID:{exceptionrole_id})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Role does not exists: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)
