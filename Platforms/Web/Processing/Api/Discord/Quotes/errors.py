from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request

async def apiDiscordQuotesNotExists(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* quote_id `str` *

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	Quote does not exists
	"""
	res:dict = dict(status=400, error="discord_quote_not_exists")

	quote_id:str = kwargs.get("quote_id", "")
	if quote_id:
		res["quote_id"] = quote_id

	default_msg:str = "Quote does not exists"

	if quote_id:
		default_msg += f" (Quote ID:{quote_id})"

	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Command not found: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)

async def apiDiscordQuoteLimit(cls:"WebIndex", WebRequest:Request, **kwargs:dict) -> Response:
	"""
	Optional keywords:
	------------------
	* msg `str` : (Default: None) * [Overwrites default]
	* limit `str`

	Default message (*gets altered by optional keywords):
	----------------------------------------------------
	You have hit the limit of quotes for this guild
	"""
	res:dict = dict(status=400, error="discord_quote_limit")

	default_msg:str = "You have hit the limit of quotes for this guild"
	msg:str = kwargs.get("msg", default_msg)
	res["msg"] = msg

	limit:str = kwargs.get("limit", cls.Web.BASE.Limit.discord_quotes_amount)
	if limit:
		res["limit"] = limit

	cls.Web.BASE.Logger.debug(f"(API/Discord) 400 Too many quotes: {WebRequest.path}", require="api:400")
	return cls.response(
		text=json.dumps( res ),
		content_type="application/json",
		status=400
	)
