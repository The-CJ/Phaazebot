from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

import json
from aiohttp.web import Response
from Utils.Classes.extendedrequest import ExtendedRequest

async def apiDiscordAlertNotExists(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* alert_id `str` *

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	Twitchalert does not exists
	"""
	res:dict = dict(status=400, error="discord_twitch_alert_not_exists")

	alert_id:str = kwargs.get("alert_id", "")
	if alert_id:
		res["alert_id"] = alert_id

	default_msg:str = "Twitchalert does not exists"
	if alert_id:
		default_msg += f" (Alert ID:{alert_id})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.BASE.Logger.debug(f"(API/Discord) 400 Twitchalert not found: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps(res),
		content_type="application/json",
		status=400
	)

async def apiDiscordAlertExists(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* alert_id `str` *
	* twitch_id `str` *
	* twitch_name `str` *
	* discord_id `str` *
	* discord_name `str` *

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	Twitchalert already exists
	"""
	res:dict = dict(status=400, error="discord_twitch_alert_exists")

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

	# build message
	default_msg:str = "Twitchalert already exists"

	if twitch_name:
		default_msg += f" for twitch channel '{twitch_name}'"
	if discord_name:
		default_msg += f" in discord channel '#{discord_name}'"

	if alert_id:
		default_msg += f" (Alert ID:{alert_id})"
	if twitch_id:
		default_msg += f" (Twitch-Channel ID:{alert_id})"
	if discord_id:
		default_msg += f" (Discord-Channel ID:{alert_id})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.BASE.Logger.debug(f"(API/Discord) 400 Twitchalert exists: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps(res),
		content_type="application/json",
		status=400
	)

async def apiDiscordAlertLimit(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* limit `str` *

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	You have hit the limit of twitchalerts
	"""
	res:dict = dict(status=400, error="discord_twitch_alert_limit")

	limit:str = kwargs.get("limit", 0) # This does not yet exists: cls.Web.BASE.Limit.DISCORD_TWITCH_AMOUNT
	if limit:
		res["limit"] = limit

	# build message
	default_msg:str = "You have hit the limit of twitchalerts"

	if limit:
		default_msg = f", the limit is {limit}"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.BASE.Logger.debug(f"(API/Discord) 400 Too many alerts: {WebRequest.path} | {msg}", require="api:400")
	return cls.response(
		text=json.dumps(res),
		content_type="application/json",
		status=400
	)

async def apiDiscordAlertSameTwitchChannelLimit(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* limit `str` *
	* twitch_name `str` *

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	You have hit the limit of same twitchalerts
	"""
	res:dict = dict(status=400, error="discord_twitch_alert_twitch_limit")

	limit:str = kwargs.get("limit", 0)
	if limit:
		res["limit"] = limit

	twitch_name:str = kwargs.get("twitch_name", "")
	if twitch_name:
		res["twitch_name"] = twitch_name

	# build message
	default_msg:str = "You have hit the limit of same twitchalerts"

	if twitch_name:
		default_msg += f" for '{twitch_name}'"

	if limit:
		default_msg += f", the limit is {limit} channels"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.BASE.Logger.debug(f"(API/Discord) 400 Too many alerts for same user: {WebRequest.path} | {msg}", require="api:400")
	return cls.response(
		text=json.dumps(res),
		content_type="application/json",
		status=400
	)
