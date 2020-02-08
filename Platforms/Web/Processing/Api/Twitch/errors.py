from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request

async def apiTwitchUserNotFound(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
			user_id:str
			user_name:str
	"""
	res:dict = dict(status=404, error="twitch_user_not_found")

	default_msg:str = "could not find a valid twitch user"
	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	user_id:str = kwargs.get("user_id", "")
	if user_id:
		res["user_id"] = user_id

	user_name:str = kwargs.get("user_name", "")
	if user_name:
		res["user_name"] = user_name

	cls.Web.BASE.Logger.debug(f"(API/Twitch) 400 User not Found: {WebRequest.path}", require="api:404")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=404
	)
