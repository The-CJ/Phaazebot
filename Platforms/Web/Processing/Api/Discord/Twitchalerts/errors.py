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

	default_msg:str = "No alert has been found"
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

async def apiDiscordAlertExists(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
			alert_id:str
			twitch_id:str
			twitch_name:str
			discord_id:str
			discord_name:str
	"""
	res:dict = dict(status=400, error="discord_twitch_alert_exists")

	default_msg:str = "The alert already exists"
	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	alert_id:str = kwargs.get("alert_id", "")
	if alert_id:
		res["alert_id"] = alert_id

	twitch_id:str = kwargs.get("twitch_id", "")
	if twitch_id:
		res["twitch_id"] = twitch_id

	twitch_name:str = kwargs.get("twitch_name", "")
	if twitch_name:
		res["twitch_name"] = twitch_name

	discord_id:str = kwargs.get("discord_id", "")
	if discord_id:
		res["discord_id"] = discord_id

	discord_name:str = kwargs.get("discord_name", "")
	if discord_name:
		res["discord_name"] = discord_name

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Twitchalert exists: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)

async def apiDiscordAlertLimit(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
			limit:str
	"""
	res:dict = dict(status=400, error="discord_twitch_alert_limit")

	default_msg:str = "You have hit the limit of alert for this guild"
	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	limit:str = kwargs.get("limit", cls.Web.BASE.Limit.DISCORD_QUOTES_AMOUNT)
	if limit:
		res["limit"] = limit

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Too many alerts: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)

async def apiDiscordAlertSameTwitchChannelLimit(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
			limit:str
			twitch_name:str
	"""
	res:dict = dict(status=400, error="discord_twitch_alert_twitch_limit")

	limit:str = kwargs.get("limit", 0)
	if limit:
		res["limit"] = limit

	twitch_name:str = kwargs.get("twitch_name", "")
	if twitch_name:
		res["twitch_name"] = twitch_name

	# build message
	default_msg:str = "You have hit the limit of same alerts for this guild"
	if limit and twitch_name:
		default_msg = f"'{twitch_name}' is already tracked in {limit} channels"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Too many alerts for same user: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)
