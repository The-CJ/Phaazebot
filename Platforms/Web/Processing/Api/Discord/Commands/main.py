from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

from aiohttp.web import Response, Request
from .get import apiDiscordCommandsGet
from Platforms.Web.Processing.Api.errors import apiMissingValidMethod

async def apiDiscordCommands(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/commands
	"""
	method:str = WebRequest.match_info.get("method", "")
	if not method: return await apiMissingValidMethod(cls, WebRequest)

	elif method == "get":
		return await apiDiscordCommandsGet(cls, WebRequest)

	else: return await apiMissingValidMethod(cls, WebRequest, msg=f"'{method}' is not a known method")
