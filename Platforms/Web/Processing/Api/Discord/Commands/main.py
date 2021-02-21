from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb
	from Platforms.Discord.main_discord import PhaazebotDiscord

from aiohttp.web import Response
from Utils.Classes.extendedrequest import ExtendedRequest
from Platforms.Web.index import PhaazeWebIndex
from Platforms.Web.Processing.Api.errors import apiMissingValidMethod, apiNotAllowed

@PhaazeWebIndex.view("/api/discord/commands{x:/?}{method:.*}")
async def apiDiscordCommands(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/commands
	"""

	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	if not PhaazeDiscord: return await apiNotAllowed(cls, WebRequest, msg="Discord module is not active")

	method:str = WebRequest.match_info.get("method", "")
	if not method: return await apiMissingValidMethod(cls, WebRequest)

	# elif method == "create":
	# 	return await apiDiscordCommandsCreate(cls, WebRequest)

	elif method == "delete":
		return await cls.Tree.Api.Discord.Commands.delete.apiDiscordCommandsDelete(cls, WebRequest)

	elif method == "edit":
		return await cls.Tree.Api.Discord.Commands.edit.apiDiscordCommandsEdit(cls, WebRequest)

	elif method == "get":
		return await cls.Tree.Api.Discord.Commands.get.apiDiscordCommandsGet(cls, WebRequest)

	elif method == "list":
		return await cls.Tree.Api.Discord.Commands.listcommands.apiDiscordCommandsListCommands(cls, WebRequest)

	else: return await apiMissingValidMethod(cls, WebRequest, msg=f"'{method}' is not a known method")
