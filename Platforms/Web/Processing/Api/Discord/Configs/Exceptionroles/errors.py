from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

import json
from aiohttp.web import Response
from Utils.Classes.extendedrequest import ExtendedRequest

async def apiDiscordExceptionRoleExists(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* role_name `str` *
	* role_id `str` *

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	Exceptionrole already exists
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

	cls.BASE.Logger.debug(f"(API/Discord) 400 Role exists: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps(res),
		content_type="application/json",
		status=400
	)

async def apiDiscordExceptionRoleNotExists(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* exceptionrole_id `str` *
	* role_id `str` *

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	Exceptionrole does not exists
	"""
	res:dict = dict(status=400, error="discord_exceptionrole_not_exists")

	exceptionrole_id:str = kwargs.get("exceptionrole_id", "")
	if exceptionrole_id:
		res["exceptionrole_id"] = str(exceptionrole_id)

	role_id:str = kwargs.get("role_id", "")
	if role_id:
		res["role_id"] = str(role_id)

	# build message
	default_msg:str = "Exceptionrole does not exists"

	if role_id:
		default_msg += f" (Role ID:{role_id})"

	if exceptionrole_id:
		default_msg += f" (Exceptionrole ID:{exceptionrole_id})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.BASE.Logger.debug(f"(API/Discord) 400 Role does not exists: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps(res),
		content_type="application/json",
		status=400
	)
