from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

from aiohttp.web import Response
from Utils.Classes.extendedrequest import ExtendedRequest
from Platforms.Web.Processing.Api.errors import apiMissingValidMethod
from Platforms.Web.index import PhaazeWebIndex

@PhaazeWebIndex.view("/api/account/phaaze{x:/?}{method:.*}")
async def apiAccountPhaaze(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/account/phaaze
	"""
	method:str = WebRequest.match_info.get("method", "")
	if not method: return await apiMissingValidMethod(cls, WebRequest)

	elif method == "get":
		return await cls.Tree.Api.Account.get.apiAccountGetPhaaze(cls, WebRequest)

	elif method == "login":
		return await cls.Tree.Api.Account.login.apiAccountLoginPhaaze(cls, WebRequest)

	elif method == "logout":
		return await cls.Tree.Api.Account.logout.apiAccountLogoutPhaaze(cls, WebRequest)

	elif method == "create":
		return await cls.Tree.Api.Account.create.apiAccountCreatePhaaze(cls, WebRequest)

	elif method == "edit":
		return await cls.Tree.Api.Account.edit.apiAccountEditPhaaze(cls, WebRequest)

	else: return await apiMissingValidMethod(cls, WebRequest, msg=f"'{method}' is not a known method")

@PhaazeWebIndex.view("/api/account/discord{x:/?}{method:.*}")
async def apiAccountDiscord(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/account/discord
	"""
	method:str = WebRequest.match_info.get("method", "")
	if not method: return await apiMissingValidMethod(cls, WebRequest)

	elif method == "get":
		return await cls.Tree.Api.Account.get.apiAccountGetDiscord(cls, WebRequest)

	elif method == "login":
		return await cls.Tree.Api.Account.login.apiAccountLoginDiscord(cls, WebRequest)

	elif method == "logout":
		return await cls.Tree.Api.Account.logout.apiAccountLogoutDiscord(cls, WebRequest)

	else: return await apiMissingValidMethod(cls, WebRequest, msg=f"'{method}' is not a known method")

@PhaazeWebIndex.view("/api/account/twitch{x:/?}{method:.*}")
async def apiAccountTwitch(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/account/twitch
	"""
	method:str = WebRequest.match_info.get("method", "")
	if not method: return await apiMissingValidMethod(cls, WebRequest)

	elif method == "get":
		return await cls.Tree.Api.Account.get.apiAccountGetTwitch(cls, WebRequest)

	elif method == "login":
		return await cls.Tree.Api.Account.login.apiAccountLoginTwitch(cls, WebRequest)

	elif method == "logout":
		return await cls.Tree.Api.Account.logout.apiAccountLogoutTwitch(cls, WebRequest)
