from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request

async def apiAdminRoleExists(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* name `str` *

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	Role already exists
	"""
	res:dict = dict(status=400, error="admin_role_exists")

	name:str = kwargs.get("name", "")
	if name:
		res["name"] = name

	# build message
	default_msg:str = "Role already exists"

	if name:
		default_msg += f" with name '{name}'"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.Web.BASE.Logger.debug(f"(API/Admin) 400 Role exits: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)

async def apiAdminRoleNotExists(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* name `str` *
	* role_id `str` *

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	No role has been found
	"""
	res:dict = dict(status=400, error="admin_role_not_exists")

	name:str = kwargs.get("name", "")
	if name:
		res["name"] = name

	role_id:str = kwargs.get("role_id", "")
	if role_id:
		res["role_id"] = role_id

	# build message
	default_msg:str = "No command has been found"

	if name:
		default_msg += f" with name '{name}'"

	if role_id:
		default_msg += f" (Role ID: {role_id})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.Web.BASE.Logger.debug(f"(API/Admin) 400 Role not found: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)
