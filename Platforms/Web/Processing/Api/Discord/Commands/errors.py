from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

import json
from aiohttp.web import Response
from Utils.Classes.extendedrequest import ExtendedRequest

async def apiDiscordCommandExists(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* trigger `str` *

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	Command already exists
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

	cls.BASE.Logger.debug(f"(API/Discord) 400 Command exits: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps(res),
		content_type="application/json",
		status=400
	)

async def apiDiscordCommandNotExists(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* trigger `str` *
	* command_id `str` *

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	No command has been found
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

	cls.BASE.Logger.debug(f"(API/Discord) 400 Command not found: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps(res),
		content_type="application/json",
		status=400
	)

async def apiDiscordCommandLimit(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* limit `str` *

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	You have hit the limit of commands for this server
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

	cls.BASE.Logger.debug(f"(API/Discord) 400 Too many commands: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps(res),
		content_type="application/json",
		status=400
	)
