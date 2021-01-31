from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

import json
from aiohttp.web import Response, Request

async def apiDiscordAssignRoleLimit(cls:"PhaazebotWeb", WebRequest:Request, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* limit `str` *

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	You have hit the limit of assign roles for this guild
	"""
	res:dict = dict(status=400, error="discord_quote_limit")

	limit:str = kwargs.get("limit", "")
	if limit:
		res["limit"] = str(limit)

	# build message
	default_msg:str = "You have hit the limit of assign roles for this guild"

	if limit:
		default_msg += f" (Limit: {limit})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.BASE.Logger.debug(f"(API/Discord) 400 Too many assign roles: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps(res),
		content_type="application/json",
		status=400
	)

async def apiDiscordAssignRoleExists(cls:"PhaazebotWeb", WebRequest:Request, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* trigger `str` *
	* role_name `str` *
	* role_id `str` *

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	Assignrole already exists
	"""
	res:dict = dict(status=400, error="discord_assignrole_exists")

	role_id:str = kwargs.get("role_id", "")
	if role_id:
		res["role_id"] = str(role_id)

	role_name:str = kwargs.get("role_name", "")
	if role_name:
		res["role_name"] = str(role_name)

	trigger:str = kwargs.get("trigger", "")
	if trigger:
		res["trigger"] = str(trigger)

	# build message
	default_msg:str = "Assignrole already exists"

	if role_name:
		default_msg += f" for role '{role_name}'"

	if trigger:
		default_msg += f" with trigger '{trigger}'"

	if role_id:
		default_msg += f" (Role ID:{role_id})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.BASE.Logger.debug(f"(API/Discord) 400 Assignrole exists: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps(res),
		content_type="application/json",
		status=400
	)

async def apiDiscordAssignRoleNotExists(cls:"PhaazebotWeb", WebRequest:Request, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* assignrole_id `str` *
	* role_id `str` *

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	Assignrole does not exists
	"""
	res:dict = dict(status=400, error="discord_assignrole_not_exists")

	assignrole_id:str = kwargs.get("assignrole_id", "")
	if assignrole_id:
		res["assignrole_id"] = str(assignrole_id)

	role_id:str = kwargs.get("role_id", "")
	if role_id:
		res["role_id"] = str(role_id)

	# build message
	default_msg:str = "Assignrole does not exists"

	if role_id:
		default_msg += f" (Role ID:{role_id})"

	if assignrole_id:
		default_msg += f" (Assignrole ID:{assignrole_id})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.BASE.Logger.debug(f"(API/Discord) 400 Assignrole not exists: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps(res),
		content_type="application/json",
		status=400
	)
