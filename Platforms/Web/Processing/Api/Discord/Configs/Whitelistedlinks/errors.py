from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

import json
from aiohttp.web import Response
from Utils.Classes.extendedrequest import ExtendedRequest

async def apiDiscordWhitelistedLinkExists(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* link `str` *

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	Whitelisted link already exists
	"""
	res:dict = dict(status=400, error="discord_whitelistlink_exists")

	link:str = kwargs.get("link", "")
	if link:
		res["link"] = str(link)

	# build message
	default_msg:str = "Whitelisted link already exists"

	if link:
		default_msg += f" (Link: '{link}')"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.BASE.Logger.debug(f"(API/Discord) 400 Link exists: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps(res),
		content_type="application/json",
		status=400
	)

async def apiDiscordWhitelistedLinkNotExists(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* link_id `str` *
	* link `str` *

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	Whitelisted link does not exists
	"""
	res:dict = dict(status=400, error="discord_whitelistlink_not_exists")

	link_id:str = kwargs.get("link_id", "")
	if link_id:
		res["link_id"] = str(link_id)

	link:str = kwargs.get("link", "")
	if link:
		res["link"] = str(link)

	# build message
	default_msg:str = "Whitelisted link does not exists"

	if link:
		default_msg += f" for '{link}')"

	if link_id:
		default_msg += f" (Link ID:{link_id})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.BASE.Logger.debug(f"(API/Discord) 400 Link does not exists: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps(res),
		content_type="application/json",
		status=400
	)
