from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request

async def apiDiscordCommandExists(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
			trigger:str
	"""
	res:dict = dict(status=400, error="discord_command_exists")

	trigger:str = kwargs.get("trigger", "")
	if trigger:
		res["trigger"] = trigger

	# build message
	default_msg:str = "Command already exists"

	if trigger:
		default_msg += f" with trigger '{trigger}'"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Command exits: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)

async def apiDiscordCommandNotExists(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
			trigger:str
			command_id:str
	"""
	res:dict = dict(status=400, error="discord_command_not_exists")

	trigger:str = kwargs.get("trigger", "")
	if trigger:
		res["trigger"] = trigger

	command_id:str = kwargs.get("command_id", "")
	if command_id:
		res["command_id"] = command_id

	# build message
	default_msg:str = "No command has been found"

	if trigger:
		default_msg += f" with trigger '{trigger}'"

	if command_id:
		default_msg += f" (Command ID: {command_id})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Command not found: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)

async def apiDiscordCommandLimit(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
			limit:str
	"""
	res:dict = dict(status=400, error="discord_command_limit")

	limit:str = kwargs.get("limit", "")
	if limit:
		res["limit"] = limit

	# build message
	default_msg:str = "You have hit the limit of commands for this server"

	if limit:
		default_msg += f" (Limit: {limit})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Too many commands: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)
