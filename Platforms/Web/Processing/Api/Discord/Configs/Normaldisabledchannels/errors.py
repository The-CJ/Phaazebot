from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

import json
from aiohttp.web import Response
from Utils.Classes.extendedrequest import ExtendedRequest

async def apiDiscordConfigsNormalDisabledChannelExists(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* channel_id `str` *
	* channel_name `str` *

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	Disabled normal channel already exists
	"""
	res:dict = dict(status=400, error="discord_disabled_normalchannel_exists")

	channel_id:str = kwargs.get("channel_id", "")
	if channel_id:
		res["channel_id"] = str(channel_id)

	channel_name:str = kwargs.get("channel_name", "")
	if channel_name:
		res["channel_name"] = str(channel_name)

	# build message
	default_msg:str = "Disabled normal channel already exists"

	if channel_name:
		default_msg += f" for '{channel_name}'"

	if channel_id:
		default_msg += f" (Channel ID:{channel_id})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.BASE.Logger.debug(f"(API/Discord) 400 Channel exists: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps(res),
		content_type="application/json",
		status=400
	)

async def apiDiscordConfigsNormalDisabledChannelNotExists(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* channel_id `str` *
	* channel_name `str` *

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	Disabled normal channel does not exists
	"""
	res:dict = dict(status=400, error="discord_disabled_normalchannel_not_exists")

	channel_id:str = kwargs.get("channel_id", "")
	if channel_id:
		res["channel_id"] = str(channel_id)

	channel_name:str = kwargs.get("channel_name", "")
	if channel_name:
		res["channel_name"] = str(channel_name)

	# build message
	default_msg:str = "Disabled normal channel does not exists"

	if channel_name:
		default_msg += f" for '{channel_name}'"

	if channel_id:
		default_msg += f" (Channel ID:{channel_id})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.BASE.Logger.debug(f"(API/Discord) 400 Channel does not exists: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps(res),
		content_type="application/json",
		status=400
	)
