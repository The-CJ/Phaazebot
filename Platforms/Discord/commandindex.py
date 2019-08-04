from typing import Awaitable

from .Processing.textonly import textOnly

command_register:list = [
	dict(
		name = "Text dummy",
		function = textOnly,
		description = "A simple text dummy that returns a predefined text",
	),
]


def getDiscordCommandFunction(command_name:str) -> Awaitable:
	"""
		get the associated function to name, else handle it as a text only
	"""
	# should not happen
	if not command_name: return textOnly

	for cmd in command_register:
		if cmd["function"].__name__ == command_name: return cmd["function"]

	return textOnly
