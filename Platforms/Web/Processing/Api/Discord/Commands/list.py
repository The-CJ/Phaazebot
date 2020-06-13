from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Discord.commandindex import command_register

async def apiDiscordCommandsList(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/commands/list
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	function:str = Data.getStr("function", "")
	detailed:bool = Data.getBool("detailed", True)

	command_list:list = []

	cmd:dict
	for cmd in sorted(command_register, key=lambda c : c["name"]):
		# user only wantes a specific command/function to be returned (could result in none)
		if function:
			if cmd["function"].__name__ != function: continue

		command:dict = dict()

		# base informations
		command["name"] = cmd.get("name", "N/A")
		command["function"] = cmd.get("function", lambda:"N/A").__name__

		if detailed:

			# extra information to know what a function wants
			command["description"] = cmd.get("description", None)
			command["arguments"] = cmd.get("arguments", list())
			command["need_content"] = cmd.get("need_content", False)
			command["allowes_content"] = cmd.get("allowes_content", False)
			command["example"] = cmd.get("example", None)

		command_list.append(command)

	return cls.response(
		text=json.dumps( dict(result=command_list, status=200) ),
		content_type="application/json",
		status=200
	)
