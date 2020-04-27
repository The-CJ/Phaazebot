from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request

async def apiDiscordUserMedalExists(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* name `str` *

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	Medal already exists
	"""
	res:dict = dict(status=400, error="discord_user_medal_exists")

	name:str = kwargs.get("name", "")
	if name:
		res["name"] = name

	# build message
	default_msg:str = "Medal already exists"

	if name:
		default_msg += f" with name '{name}'"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Medal exits: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)

async def apiDiscordUserMedalNotExists(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* medal_id `str` *
	* name `str` *

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	No command has been found
	"""
	res:dict = dict(status=400, error="discord_user_medal_not_exists")

	medal_id:str = kwargs.get("medal_id", "")
	if medal_id:
		res["medal_id"] = medal_id

	name:str = kwargs.get("name", "")
	if name:
		res["name"] = name

	# build message
	default_msg:str = "No Medal has been found"

	if name:
		default_msg += f" with name '{name}'"

	if medal_id:
		default_msg += f" (Medal ID: {medal_id})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Command not found: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)

async def apiDiscordUserMedalLimit(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* limit `str` *

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	You have hit the limit of medals for this member
	"""
	res:dict = dict(status=400, error="discord_user_medal_limit")

	limit:str = kwargs.get("limit", "")
	if limit:
		res["limit"] = limit

	# build message
	default_msg:str = "You have hit the limit of medals for this member"

	if limit:
		default_msg += f" (Limit: {limit})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Too many medals: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)
