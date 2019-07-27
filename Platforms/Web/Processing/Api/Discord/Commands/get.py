from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Web.Processing.Api.errors import missingData
from Platforms.Discord.utils import getDiscordServerCommands

async def apiDiscordCommandsGet(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/commands/get
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	guild_id:str = Data.get("guild_id")
	if not guild_id:
		return await missingData(cls, WebRequest, msg="missing 'guild_id'")

	command_id:str = Data.get("command_id")
	if not command_id:
		command_id = None

	commands:list = await getDiscordServerCommands(cls.Web.BASE.Discord, guild_id, command_id=command_id)

	api_return:list = list()
	for command in commands:

		cmd:dict = dict(
			trigger = command.trigger,
			content = command.content if not command.hidden else None,
			function = command.function if not command.hidden else None,
			complex = command.complex,
			cost = command.required_currency,
			uses = command.uses,
			require = command.require,
			hidden = command.hidden,
			id=command.command_id
		)

		api_return.append(cmd)

	return cls.response(
		text=json.dumps( dict(result=api_return, status=200) ),
		content_type="application/json",
		status=200
	)
