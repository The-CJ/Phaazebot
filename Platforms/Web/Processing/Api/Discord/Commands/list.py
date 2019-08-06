from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request
from Platforms.Discord.commandindex import command_register
from Utils.Classes.webrequestcontent import WebRequestContent

async def apiDiscordCommandsList(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/commands/list
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	function:str = Data.get("function")

	command_list:list = []

	for cmd in command_register:
		# user only wantes a specific command/function to be returned (could result in none)
		if function:
			if cmd["function"].__name__ != function: continue

		c:dict = dict(
			name = cmd["name"],
			description = cmd["description"],
			function = cmd["function"].__name__,
			details = cmd["details"]
		)

		command_list.append(c)

	return cls.response(
		text=json.dumps( dict(result=command_list, status=200) ),
		content_type="application/json",
		status=200
	)
