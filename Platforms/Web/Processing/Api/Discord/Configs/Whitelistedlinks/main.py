from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.main_web import PhaazebotWeb

from aiohttp.web import Response
from Utils.Classes.extendedrequest import ExtendedRequest
from Platforms.Web.index import PhaazeWebIndex
from Platforms.Web.Processing.Api.errors import apiMissingValidMethod, apiNotAllowed

@PhaazeWebIndex.view("/api/discord/configs/whitelistedlinks{x:/?}{method:.*}")
async def apiDiscordConfigsWhitelistedLink(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/configs/whitelistedlinks
	"""

	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	if not PhaazeDiscord: return await apiNotAllowed(cls, WebRequest, msg="Discord module is not active")

	method:str = WebRequest.match_info.get("method", "")
	if not method: return await apiMissingValidMethod(cls, WebRequest)

	# elif method == "create":
	# 	return await apiDiscordConfigsWhitelistedLinkCreate(cls, WebRequest)

	# elif method == "delete":
	# 	return await apiDiscordConfigsWhitelistedLinkDelete(cls, WebRequest)

	elif method == "get":
		return await cls.Tree.Api.Discord.Configs.Whitelistedlinks.get.apiDiscordConfigsWhitelistedLinkGet(cls, WebRequest)

	else: return await apiMissingValidMethod(cls, WebRequest, msg=f"'{method}' is not a known method")
