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

	alert_id:str = kwargs.get("alert_id", "")
	if alert_id:
		res["alert_id"] = alert_id

	default_msg:str = "No twitchalert has been found"
	if alert_id:
		default_msg += f" (Alert ID:{alert_id})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

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
	default_msg:str = "The twitchalert already exists"

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
			guild_id:str
			guild_name:str
	"""
	res:dict = dict(status=400, error="discord_twitch_alert_limit")

	limit:str = kwargs.get("limit", 0) # This does not yet exists: cls.Web.BASE.Limit.DISCORD_TWITCH_AMOUNT
	if limit:
		res["limit"] = limit

	guild_id:str = kwargs.get("guild_id", "")
	if guild_id:
		res["guild_id"] = guild_id

	guild_name:str = kwargs.get("guild_name", "")
	if guild_name:
		res["guild_name"] = guild_name

	# build message
	default_msg:str = "You have hit the limit of twitchalerts"

	if guild_name:
		default_msg += f" on guild '{guild_name}'"
	if limit:
		default_msg = f", the limit is {limit}"

	if guild_id:
		default_msg = f" (Guild ID:{guild_id})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Too many alerts: {WebRequest.path} | {msg}", require="api:400")
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
			guild_id:str
			guild_name:str
			twitch_name:str
	"""
	res:dict = dict(status=400, error="discord_twitch_alert_twitch_limit")

	limit:str = kwargs.get("limit", 0)
	if limit:
		res["limit"] = limit

	guild_id:str = kwargs.get("guild_id", "")
	if guild_id:
		res["guild_id"] = guild_id

	guild_name:str = kwargs.get("guild_name", "")
	if guild_name:
		res["guild_name"] = guild_name

	twitch_name:str = kwargs.get("twitch_name", "")
	if twitch_name:
		res["twitch_name"] = twitch_name

	# build message
	default_msg:str = "You have hit the limit of same twitchalerts"

	if guild_name:
		default_msg += f" on guild '{guild_name}'"
	if twitch_name:
		default_msg = f" for Twitch channel '{twitch_name}'"
	if limit:
		default_msg = f", the limit is {limit} channels"

	if guild_id:
		default_msg = f" (Guild ID:{guild_id})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Too many alerts for same user: {WebRequest.path} | {msg}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)
