from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

import json
from aiohttp.web import Response, Request

async def apiDiscordRegularExists(cls:"PhaazebotWeb", WebRequest:Request, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* regular_id `str` *

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	Regular already exists
	"""
	res:dict = dict(status=400, error="discord_regular_exists")

	regular_id:str = kwargs.get("regular_id", "")
	if regular_id:
		res["regular_id"] = regular_id

	default_msg:str = "Regular already exists"

	if regular_id:
		default_msg += f" (Regular ID:{regular_id})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.BASE.Logger.debug(f"(API/Discord) 400 Regular exists: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps(res),
		content_type="application/json",
		status=400
	)

async def apiDiscordRegularNotExists(cls:"PhaazebotWeb", WebRequest:Request, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* regular_id `str` *

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	Regular does not exists
	"""
	res:dict = dict(status=400, error="discord_regular_not_exists")

	regular_id:str = kwargs.get("regular_id", "")
	if regular_id:
		res["regular_id"] = regular_id

	default_msg:str = "Regular does not exists"

	if regular_id:
		default_msg += f" (Regular ID:{regular_id})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.BASE.Logger.debug(f"(API/Discord) 400 Regular does not exists: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps(res),
		content_type="application/json",
		status=400
	)

async def apiDiscordRegularLimit(cls:"PhaazebotWeb", WebRequest:Request, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* limit `str`

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	You have hit the limit of regulars for this guild
	"""
	res:dict = dict(status=400, error="discord_regular_limit")

	default_msg:str = "You have hit the limit of regulars for this guild"
	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	limit:str = kwargs.get("limit", cls.BASE.Limit.discord_regular_amount)
	if limit:
		res["limit"] = limit

	cls.BASE.Logger.debug(f"(API/Discord) 400 Too many regulars: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps(res),
		content_type="application/json",
		status=400
	)
