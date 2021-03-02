from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.main_web import PhaazebotWeb

from aiohttp.web import Response
from Utils.Classes.extendedrequest import ExtendedRequest
from Platforms.Web.Processing.Api.errors import apiMissingValidMethod, apiNotAllowed

async def apiDiscordConfigsBlacklistedWords(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/configs/blacklistedwords
	"""

	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	if not PhaazeDiscord: return await apiNotAllowed(cls, WebRequest, msg="Discord module is not active")

	method:str = WebRequest.match_info.get("method", "")
	if not method: return await apiMissingValidMethod(cls, WebRequest)

	elif method == "create": # TODO
		return await cls.Tree.Api.Discord.Configs.Blacklistedwords.create.apiDiscordConfigsBlacklistedWordsCreate(cls, WebRequest)

	elif method == "delete": # TODO
		return await cls.Tree.Api.Discord.Configs.Blacklistedwords.delete.apiDiscordConfigsBlacklistedWordsDelete(cls, WebRequest)

	elif method == "get": # TODO
		return await cls.Tree.Api.Discord.Configs.Blacklistedwords.get.apiDiscordConfigsBlacklistedWordsGet(cls, WebRequest)

	else: return await apiMissingValidMethod(cls, WebRequest, msg=f"'{method}' is not a known method")
