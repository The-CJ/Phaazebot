from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.index import WebIndex

from aiohttp.web import Response, Request
from .create import apiDiscordConfigsNsfwEnabledChannelsCreate
from .delete import apiDiscordConfigsNsfwEnabledChannelsDelete
from .get import apiDiscordConfigsNsfwEnabledChannelsGet
from Platforms.Web.Processing.Api.errors import apiMissingValidMethod, apiNotAllowed

async def apiDiscordConfigsNsfwEnabledChannels(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/configs/nsfwenabledchannels
	"""

	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	if not PhaazeDiscord: return await apiNotAllowed(cls, WebRequest, msg="Discord module is not active")

	method:str = WebRequest.match_info.get("method", "")
	if not method: return await apiMissingValidMethod(cls, WebRequest)

	elif method == "create":
		return await apiDiscordConfigsNsfwEnabledChannelsCreate(cls, WebRequest)

	elif method == "delete":
		return await apiDiscordConfigsNsfwEnabledChannelsDelete(cls, WebRequest)

	elif method == "get":
		return await apiDiscordConfigsNsfwEnabledChannelsGet(cls, WebRequest)

	else: return await apiMissingValidMethod(cls, WebRequest, msg=f"'{method}' is not a known method")
