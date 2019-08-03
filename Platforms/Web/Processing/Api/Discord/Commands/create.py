from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Web.Processing.Api.errors import missingData
from Platforms.Discord.utils import getDiscordServerCommands

async def apiDiscordCommandsCreate(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/commands/create
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	guild_id:str = Data.get("guild_id")
	if not guild_id:
		return await missingData(cls, WebRequest, msg="missing 'guild_id'")

	commands:list = await getDiscordServerCommands(cls.Web.BASE.Discord, guild_id)
	print(len(commands))

	return cls.response(
		text=json.dumps( dict(result="", status=200) ),
		content_type="application/json",
		status=200
	)
