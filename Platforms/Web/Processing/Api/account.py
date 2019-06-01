from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

from aiohttp.web import Response, Request
from .errors import apiNotAllowed, apiMissingValidMethod
from .accountget import apiAccountPhaazeGet, apiAccountDiscordGet, apiAccountTwitchGet
from .accountlogin import apiAccountPhaazeLogin, apiAccountDiscordLogin, apiAccountTwitchLogin

async def apiAccountPhaaze(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/phaaze
	"""
	method:str = WebRequest.match_info.get("method", "")
	if not method: return await apiMissingValidMethod(cls, WebRequest)

	elif method == "get":
		return await apiAccountPhaazeGet(cls, WebRequest)

	elif method == "login":
		return await apiAccountPhaazeLogin(cls, WebRequest)

	else: return await apiMissingValidMethod(cls, WebRequest, msg=f"'{method}' is not a known method")

async def apiAccountDiscord(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/discord
	"""
	return await apiNotAllowed(cls, WebRequest, msg="Under construction")
	return await apiAccountDiscordLogin(cls, WebRequest)
	return await apiAccountDiscordGet(cls, WebRequest)

async def apiAccountTwitch(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/twitch
	"""
	return await apiNotAllowed(cls, WebRequest, msg="Under construction")
	return await apiAccountTwitchLogin(cls, WebRequest)
	return await apiAccountTwitchGet(cls, WebRequest)
