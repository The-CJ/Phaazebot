from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.index import WebIndex

from aiohttp.web import Response, Request
from .get import apiDiscordCommandsGet
from .create import apiDiscordCommandsCreate
from .list import apiDiscordCommandsList
from .delete import apiDiscordCommandsDelete
from .edit import apiDiscordCommandsEdit
from Platforms.Web.Processing.Api.errors import apiMissingValidMethod, apiNotAllowed

async def apiDiscordCommands(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/commands
	"""

	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	if not PhaazeDiscord: return await apiNotAllowed(cls, WebRequest, msg="Discord module is not active")

	method:str = WebRequest.match_info.get("method", "")
	if not method: return await apiMissingValidMethod(cls, WebRequest)

	elif method == "get":
		return await apiDiscordCommandsGet(cls, WebRequest)

	elif method == "delete":
		return await apiDiscordCommandsDelete(cls, WebRequest)

	elif method == "create":
		return await apiDiscordCommandsCreate(cls, WebRequest)

	elif method == "edit":
		return await apiDiscordCommandsEdit(cls, WebRequest)

	elif method == "list":
		return await apiDiscordCommandsList(cls, WebRequest)

	else: return await apiMissingValidMethod(cls, WebRequest, msg=f"'{method}' is not a known method")
