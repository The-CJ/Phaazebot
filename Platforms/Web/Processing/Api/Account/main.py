from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

from aiohttp.web import Response, Request
from Platforms.Web.Processing.Api.errors import apiNotAllowed, apiMissingValidMethod
from .get import apiAccountGetPhaaze, apiAccountGetDiscord, apiAccountGetTwitch
from .login import apiAccountLoginPhaaze, apiAccountLoginDiscord, apiAccountLoginTwitch
from .logout import apiAccountLogoutPhaaze, apiAccountLogoutDiscord, apiAccountLogoutTwitch
from .create import apiAccountCreatePhaaze
from .edit import apiAccountEditPhaaze

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

	elif method == "logout":
		return await apiAccountLogoutPhaaze(cls, WebRequest)

	elif method == "create":
		return await apiAccountCreatePhaaze(cls, WebRequest)

	elif method == "edit":
		return await apiAccountEditPhaaze(cls, WebRequest)

	else: return await apiMissingValidMethod(cls, WebRequest, msg=f"'{method}' is not a known method")

async def apiAccountDiscord(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/discord
	"""
	method:str = WebRequest.match_info.get("method", "")
	if not method: return await apiMissingValidMethod(cls, WebRequest)

	elif method == "get":
		return await apiAccountGetDiscord(cls, WebRequest)

	elif method == "login":
		return await apiAccountLoginDiscord(cls, WebRequest)

	elif method == "logout":
		return await apiAccountLogoutDiscord(cls, WebRequest)

	else: return await apiMissingValidMethod(cls, WebRequest, msg=f"'{method}' is not a known method")


async def apiAccountTwitch(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/twitch
	"""
	return await apiNotAllowed(cls, WebRequest, msg="Under construction")
	return await apiAccountGetTwitch(cls, WebRequest)
	return await apiAccountLoginTwitch(cls, WebRequest)
	return await apiAccountLogoutTwitch(cls, WebRequest)
