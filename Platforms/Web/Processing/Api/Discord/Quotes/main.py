from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.index import WebIndex

from aiohttp.web import Response, Request
from .get import apiDiscordQuotesGet
from .edit import apiDiscordQuotesEdit
from .create import apiDiscordQuotesCreate
from .delete import apiDiscordQuotesDelete
from Platforms.Web.Processing.Api.errors import apiMissingValidMethod, apiNotAllowed

async def apiDiscordQuotes(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/quotes
	"""

	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	if not PhaazeDiscord: return await apiNotAllowed(cls, WebRequest, msg="Discord module is not active")

	method:str = WebRequest.match_info.get("method", "")
	if not method: return await apiMissingValidMethod(cls, WebRequest)

	elif method == "get":
		return await apiDiscordQuotesGet(cls, WebRequest)

	elif method == "edit":
		return await apiDiscordQuotesEdit(cls, WebRequest)

	elif method == "create":
		return await apiDiscordQuotesCreate(cls, WebRequest)

	elif method == "delete":
		return await apiDiscordQuotesDelete(cls, WebRequest)

	else: return await apiMissingValidMethod(cls, WebRequest, msg=f"'{method}' is not a known method")
