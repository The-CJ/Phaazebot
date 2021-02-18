from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import PhaazeWebIndex

import json
from aiohttp.web import Response
from Utils.Classes.extendedrequest import ExtendedRequest

async def apiDiscordLevelMedalLimit(cls:"PhaazeWebIndex", WebRequest:ExtendedRequest, **kwargs) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* limit `str`

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	You have hit the limit of medals for this member
	"""
	res:dict = dict(status=400, error="discord_medal_limit")

	default_msg:str = "You have hit the limit of medals for this member"
	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	limit:str = kwargs.get("limit", cls.Web.BASE.Limit.discord_level_medal_amount)
	if limit:
		res["limit"] = limit

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Too many medals: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps(res),
		content_type="application/json",
		status=400
	)
