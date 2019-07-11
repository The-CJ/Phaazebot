from typing import Awaitable

from .Processing.Simple.textonly import textOnly

register:dict = dict(
	textOnly = textOnly,


)

def getDiscordCommandFunction(function_type:str, command_name:str) -> Awaitable:
	"""
		get the associated function to name, else hanbdle it a text only
	"""
	# should not happen
	if not command_name: return textOnly

	return register.get(command_name, textOnly)
