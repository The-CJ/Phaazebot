from typing import Awaitable
from Utils.Classes.storeclasses import GlobalStorage

from .Processing.textonly import textOnly
from .Processing.listcommands import listCommands

command_register:list = [
	dict(
		name = "Text dummy",
		function = textOnly,
		description = "A simple text dummy that returns a predefined text",
		details = "This command requires a content, this content supports placeholder variables",
		need_content = True
	),
	dict(
		name = "List commands",
		function = listCommands,
		description = "List all commands a server has, also provides a link to the public command website",
		details = "It only shows the first 20 commands, after that it only says there are more. Else it would be to spammy",
		need_content = False
	),
]

GlobalStorage.add("discord_command_register", command_register)

def getDiscordCommandFunction(command_name:str) -> Awaitable:
	"""
		get the associated function to name, else handle it as a text only
	"""
	# should not happen
	if not command_name: return textOnly

	for cmd in command_register:
		if cmd["function"].__name__ == command_name: return cmd["function"]

	return textOnly
