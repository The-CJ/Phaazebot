from typing import Awaitable
from Utils.Classes.storeclasses import GlobalStorage

from .Processing.textonly import textOnly
from .Processing.listcommands import listCommands
from .Processing.showquote import showQuote
from .Processing.addquote import addQuote
from .Processing.randomchoice import randomChoice
from .Processing.urbandictionary import urbanDictionary
from .Processing.whois import whois

command_register:list = [
	dict(
		name = "Text dummy",
		function = textOnly,
		description = "A simple text dummy that returns a predefined text, it requires a content,\n"\
			"this content supports placeholder variables",
		details = "This command does not take any arguments",
		need_content = True
	),
	dict(
		name = "List commands",
		function = listCommands,
		description = "List all commands a server has, also provides a link to the public command website\n"\
			"It only shows the first 20 commands, after that it only says there are more. Else it would be to spammy",
		details = "This command does not take any arguments",
		need_content = False
	),
	dict(
		name = "Show quote",
		function = showQuote,
		description = "If not defined otherwise, it returns a random quote from this server",
		details = "This function takes one 1 optional argument.\n"\
			"(1) ID of the quote you want.",
		need_content = False
	),
	dict(
		name = "Add quote",
		function = addQuote,
		description = "Adds a new quote to the server quote list.\n"\
			"(It's highly recommended to set the requirement higher than Everyone)",
		details = "This function takes everything after the trigger.\n"\
			"and makes it the new quote.",
		need_content = False
	),
	dict(
		name = "Random choise",
		function = randomChoice,
		description = "Takes all arguments after the command, sepparated by ;\n"\
			"Gives back one of the splittet content",
		details = "This function takes everything after the trigger.\n"\
			"and sepperated by ;",
		need_content = False
	),
	dict(
		name = "Urban define",
		function = urbanDictionary,
		description = "Uses UrbanDictionary to get a difination for your input",
		details = "This function takes everything after the trigger and tryed to define it",
		need_content = False
	),
	dict(
		name = "Whois",
		function = whois,
		description = "Gives a summary of a user, with everything he has\n"\
			"(does not include EXP and Currency, these are sepperate commands)",
		details = "This function takes one 1 optional argument\n"\
			"(1) Query string to search a user: Name, id, Mention or None for the command caller",
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
