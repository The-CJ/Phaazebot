from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

import json
from aiohttp.web import Response
from Utils.Classes.extendedrequest import ExtendedRequest

async def apiTwitchUserNotFound(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* user_id `str` *
	* user_name `str` *

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	Could not find a valid twitch user
	"""
	res:dict = dict(status=404, error="twitch_user_not_found")

	user_id:str = kwargs.get("user_id", "")
	if user_id:
		res["user_id"] = user_id

	user_name:str = kwargs.get("user_name", "")
	if user_name:
		res["user_name"] = user_name

	default_msg:str = "Could not find a valid twitch user"

	if user_name:
		default_msg += f" with name: '{user_name}'"

	if user_id:
		default_msg += f" (User ID:{user_id})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.BASE.Logger.debug(f"(API/Twitch) 400 User not Found: {WebRequest.path}", require="api:404")
	return cls.response(
		text=json.dumps(res),
		content_type="application/json",
		status=404
	)
