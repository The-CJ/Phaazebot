from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.index import WebIndex

from aiohttp.web import Response, Request
from .get import apiDiscordAssignrolesGet
from .create import apiDiscordAssignrolesCreate
from .edit import apiDiscordAssignrolesEdit
from .delete import apiDiscordAssignrolesDelete
from Platforms.Web.Processing.Api.errors import apiMissingValidMethod, apiNotAllowed

async def apiDiscordAssignroles(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/assignroles
	"""

	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	if not PhaazeDiscord: return await apiNotAllowed(cls, WebRequest, msg="Discord module is not active")

	method:str = WebRequest.match_info.get("method", "")
	if not method: return await apiMissingValidMethod(cls, WebRequest)

	elif method == "get":
		return await apiDiscordAssignrolesGet(cls, WebRequest)

	elif method == "create":
		return await apiDiscordAssignrolesCreate(cls, WebRequest)

	elif method == "edit":
		return await apiDiscordAssignrolesEdit(cls, WebRequest)

	elif method == "delete":
		return await apiDiscordAssignrolesDelete(cls, WebRequest)

	else: return await apiMissingValidMethod(cls, WebRequest, msg=f"'{method}' is not a known method")
