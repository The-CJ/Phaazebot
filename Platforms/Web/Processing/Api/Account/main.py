from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

from aiohttp.web import Response
from Utils.Classes.extendedrequest import ExtendedRequest
from Platforms.Web.Processing.Api.errors import apiMissingValidMethod
from Platforms.Web.index import PhaazeWebIndex

from Platforms.Web.Processing.Api.Account.get import apiAccountGetPhaaze, apiAccountGetDiscord, apiAccountGetTwitch
from Platforms.Web.Processing.Api.Account.login import apiAccountLoginPhaaze, apiAccountLoginDiscord, apiAccountLoginTwitch
from Platforms.Web.Processing.Api.Account.logout import apiAccountLogoutPhaaze, apiAccountLogoutDiscord, apiAccountLogoutTwitch
from Platforms.Web.Processing.Api.Account.create import apiAccountCreatePhaaze
from Platforms.Web.Processing.Api.Account.edit import apiAccountEditPhaaze

@PhaazeWebIndex.view("/api/account/phaaze{x:/?}{method:.*}")
async def apiAccountPhaaze(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
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

@PhaazeWebIndex.view("/api/account/discord{x:/?}{method:.*}")
async def apiAccountDiscord(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
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

@PhaazeWebIndex.view("/api/account/twitch{x:/?}{method:.*}")
async def apiAccountTwitch(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/account/twitch
	"""
	method:str = WebRequest.match_info.get("method", "")
	if not method: return await apiMissingValidMethod(cls, WebRequest)

	elif method == "get":
		return await apiAccountGetTwitch(cls, WebRequest)

	elif method == "login":
		return await apiAccountLoginTwitch(cls, WebRequest)

	elif method == "logout":
		return await apiAccountLogoutTwitch(cls, WebRequest)
