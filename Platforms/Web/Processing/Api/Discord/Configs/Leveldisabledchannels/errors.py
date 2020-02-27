from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request

async def apiDiscordConfigsLevelDisabledChannelExists(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
			channel_id:str
			channel_name:str
	"""
	res:dict = dict(status=400, error="discord_disabled_levelchannel_exists")

	channel_id:str = kwargs.get("channel_id", "")
	if channel_id:
		res["channel_id"] = str(channel_id)

	channel_name:str = kwargs.get("channel_name", "")
	if channel_name:
		res["channel_name"] = str(channel_name)

	# build message
	default_msg:str = "Disabled level channel already exists"

	if channel_name:
		default_msg += f" for '{channel_name}'"

	if channel_id:
		default_msg += f" (Channel ID:{channel_id})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Channel exists: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)

async def apiDiscordConfigsLevelDisabledChannelNotExists(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
		Takes from kwargs:
			msg:str
			channel_id:str
			channel_name:str
	"""
	res:dict = dict(status=400, error="discord_disabled_levelchannel_not_exists")

	channel_id:str = kwargs.get("channel_id", "")
	if channel_id:
		res["channel_id"] = str(channel_id)

	channel_name:str = kwargs.get("channel_name", "")
	if channel_name:
		res["channel_name"] = str(channel_name)

	# build message
	default_msg:str = "No disabled level channel found"

	if channel_name:
		default_msg += f" for '{channel_name}'"

	if channel_id:
		default_msg += f" (Channel ID:{channel_id})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Channel does not exists: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)
