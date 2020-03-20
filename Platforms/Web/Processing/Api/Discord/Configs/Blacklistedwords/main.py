from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.index import WebIndex

from aiohttp.web import Response, Request
from .create import apiDiscordConfigsBlacklistedWordsCreate
from .delete import apiDiscordConfigsBlacklistedWordsDelete
from .get import apiDiscordConfigsBlacklistedWordsGet
from Platforms.Web.Processing.Api.errors import apiMissingValidMethod, apiNotAllowed

async def apiDiscordConfigsBlacklistedWords(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/configs/blacklistedwords
	"""

	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	if not PhaazeDiscord: return await apiNotAllowed(cls, WebRequest, msg="Discord module is not active")

	method:str = WebRequest.match_info.get("method", "")
	if not method: return await apiMissingValidMethod(cls, WebRequest)

	elif method == "create":
		return await apiDiscordConfigsBlacklistedWordsCreate(cls, WebRequest)

	elif method == "delete":
		return await apiDiscordConfigsBlacklistedWordsDelete(cls, WebRequest)

	elif method == "get":
		return await apiDiscordConfigsBlacklistedWordsGet(cls, WebRequest)

	else: return await apiMissingValidMethod(cls, WebRequest, msg=f"'{method}' is not a known method")
