from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request

async def apiDiscordAssignRoleLimit(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
			limit:str
	"""
	res:dict = dict(status=400, error="discord_quote_limit")

	default_msg:str = "You have hit the limit of assign roles for this guild"
	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	limit:str = kwargs.get("limit", cls.Web.BASE.Limit.DISCORD_ASSIGNROLE_AMOUNT)
	if limit:
		res["limit"] = limit

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Too many assign roles: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)

async def apiDiscordAssignRoleExists(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
			role_id:str
			trigger:str
	"""
	res:dict = dict(status=400, error="discord_assignrole_exists")

	default_msg:str = "Assignrole already exists"
	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	role_id:str = kwargs.get("role_id", "")
	if role_id:
		res["role_id"] = role_id

	trigger:str = kwargs.get("trigger", "")
	if trigger:
		res["trigger"] = trigger

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Assignrole exists: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)

async def apiDiscordAssignRoleNotExists(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
			assignrole_id:str
	"""
	res:dict = dict(status=400, error="discord_assignrole_not_exists")

	default_msg:str = "Assignrole does not exists"
	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	assignrole_id:str = kwargs.get("assignrole_id", "")
	if assignrole_id:
		res["assignrole_id"] = assignrole_id

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Assignrole not exists: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)
