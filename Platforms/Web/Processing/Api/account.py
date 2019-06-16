from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

from aiohttp.web import Response, Request
from .errors import apiNotAllowed, apiMissingValidMethod
from .Account.get import apiAccountGetPhaaze, apiAccountGetDiscord, apiAccountGetTwitch
from .Account.login import apiAccountLoginPhaaze, apiAccountLoginDiscord, apiAccountLoginTwitch

async def apiAccountPhaaze(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/phaaze
	"""
	method:str = WebRequest.match_info.get("method", "")
	if not method: return await apiMissingValidMethod(cls, WebRequest)

	elif method == "get":
		return await apiAccountGetPhaaze(cls, WebRequest)

	elif method == "login":
		return await apiAccountLoginPhaaze(cls, WebRequest)

	else: return await apiMissingValidMethod(cls, WebRequest, msg=f"'{method}' is not a known method")

async def apiAccountDiscord(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/discord
	"""
	return await apiNotAllowed(cls, WebRequest, msg="Under construction")
	return await apiAccountLoginDiscord(cls, WebRequest)
	return await apiAccountGetDiscord(cls, WebRequest)

async def apiAccountTwitch(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/twitch
	"""
	return await apiNotAllowed(cls, WebRequest, msg="Under construction")
	return await apiAccountLoginTwitch(cls, WebRequest)
	return await apiAccountGetTwitch(cls, WebRequest)
