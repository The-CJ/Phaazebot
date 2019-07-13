from typing import Awaitable

from .Processing.Simple.register import  simple_register
from .Processing.Complex.register import complex_register
from .Processing.Simple.textonly import textOnly as standardCommandFunction

def getDiscordCommandFunction(function_type:str, command_name:str) -> Awaitable:
	"""
		get the associated function to name, else hanbdle it a text only
	"""
	# should not happen
	if not command_name: return standardCommandFunction

	if function_type == "simple":
		return simple_register.get(command_name, standardCommandFunction)

	elif function_type == "complex":
		return complex_register.get(command_name, standardCommandFunction)

	else:
		return standardCommandFunction
