from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.index import WebIndex

from aiohttp.web import Response, Request
from .create import apiDiscordLevelsMedalsCreate
from .delete import apiDiscordLevelsMedalsDelete
from .get import apiDiscordLevelsMedalsGet
from Platforms.Web.Processing.Api.errors import apiMissingValidMethod, apiNotAllowed

async def apiDiscordLevelsMedals(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/levels/medals
	"""

	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	if not PhaazeDiscord: return await apiNotAllowed(cls, WebRequest, msg="Discord module is not active")

	method:str = WebRequest.match_info.get("method", "")
	if not method: return await apiMissingValidMethod(cls, WebRequest)

	elif method == "create":
		return await apiDiscordLevelsMedalsCreate(cls, WebRequest)

	elif method == "delete":
		return await apiDiscordLevelsMedalsDelete(cls, WebRequest)

	elif method == "get":
		return await apiDiscordLevelsMedalsGet(cls, WebRequest)

	else: return await apiMissingValidMethod(cls, WebRequest, msg=f"'{method}' is not a known method")
