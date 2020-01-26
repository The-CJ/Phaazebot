from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request

async def apiDiscordCommandExists(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
			command:str
	"""
	res:dict = dict(status=400, error="discord_command_exists")

	default_msg:str = "This command trigger already exists"
	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	command:str = kwargs.get("command", "")
	if command:
		res["command"] = command

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
			command:str
	"""
	res:dict = dict(status=400, error="discord_command_not_exists")

	default_msg:str = "No command has been found"
	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	command:str = kwargs.get("command", "")
	if command:
		res["command"] = command

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

	default_msg:str = "You have hit the limit of commands for this server"
	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	limit:str = kwargs.get("limit", cls.Web.BASE.Limit.DISCORD_COMMANDS_AMOUNT)
	if limit:
		res["limit"] = limit

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Too many commands: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)
