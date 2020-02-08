from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request

async def apiDiscordAlertNotExists(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
			alert_id:str
	"""
	res:dict = dict(status=400, error="discord_twitch_alert_not_exists")

	default_msg:str = "No quote has been found"
	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	alert_id:str = kwargs.get("alert_id", "")
	if alert_id:
		res["alert_id"] = alert_id

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Twitchalert not found: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)
