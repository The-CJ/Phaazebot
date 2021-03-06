from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

import json
from aiohttp.web import Response
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Discord.commandindex import command_register
from Utils.Classes.extendedrequest import ExtendedRequest

async def apiDiscordCommandsListCommands(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/commands/list
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	function:str = Data.getStr("function", "", len_max=128)
	detailed:bool = Data.getBool("detailed", True)
	recommended:bool = Data.getBool("recommended", False)

	command_list:list = []

	cmd:dict
	for cmd in sorted(command_register, key=lambda c: c["name"]):
		# user only wants a specific command/function to be returned (could result in none)
		if function:
			if cmd["function"].__name__ != function: continue

		command:dict = dict()

		# base information
		command["name"] = cmd.get("name", "N/A")
		command["function"] = cmd.get("function", lambda:"N/A").__name__

		if detailed:

			# extra information to know what a function wants
			command["description"] = cmd.get("description", None)
			command["required_arguments"] = cmd.get("required_arguments", [])
			command["optional_arguments"] = cmd.get("optional_arguments", [])
			command["endless_arguments"] = cmd.get("endless_arguments", False)
			command["need_content"] = cmd.get("need_content", False)
			command["allows_content"] = cmd.get("allows_content", False)
			command["example_calls"] = cmd.get("example_calls", [])

		if recommended:

			# recommended values for a command
			command["recommended_require"] = cmd.get("recommended_require", None)
			command["recommended_cooldown"] = cmd.get("recommended_cooldown", None)

		command_list.append(command)

	return cls.response(
		text=json.dumps(dict(result=command_list, status=200)),
		content_type="application/json",
		status=200
	)
