from typing import Awaitable
from Utils.Classes.storeclasses import GlobalStorage

from .Processing.textonly import textOnly
from .Processing.listcommands import listCommands
from .Processing.showquote import showQuote
from .Processing.addquote import addQuote
from .Processing.removequote import removeQuote
from .Processing.randomchoice import randomChoice
from .Processing.urbandictionary import urbanDictionary
from .Processing.whois import whois
from .Processing.prunemessages import pruneMessages
from .Processing.wikipedia import searchWikipedia
from .Processing.osustatus import osuStats
from .Processing.listassignrole import listAssignRole
from .Processing.addassignrole import addAssignRole
from .Processing.removeassignrole import removeAssignRole
from .Processing.assignrole import assignRole
from .Processing.levelstatus import levelStatus
from .Processing.levelleaderboard import levelLeaderboard

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
		name = "Commands | List",
		function = listCommands,
		description = "List all commands a server has, also provides a link to the public command website\n"\
			"It only shows the first 20 commands, after that it only says there are more. Else it would be to spammy",
		details = "This command does not take any arguments",
		need_content = False
	),
	dict(
		name = "Quote | Show",
		function = showQuote,
		description = "If not defined otherwise, it returns a random quote from this server",
		details = "This function takes one 1 optional argument.\n"\
			"(1) ID of the quote you want.",
		need_content = False
	),
	dict(
		name = "Quote | Add",
		function = addQuote,
		description = "Adds a new quote to the server quote list.\n"\
			"(It's highly recommended to set the requirement higher than Everyone)",
		details = "This function takes everything after the trigger.\n"\
			"and makes it the new quote.",
		need_content = False
	),
	dict(
		name = "Quote | Remove",
		function = removeQuote,
		description = "Removes a quote from the server quote list.\n"\
			"(It's highly recommended to set the requirement higher than Everyone)",
		details = "This function takes one 1 required argument.\n"\
			"[1] The Quote ID to delete.",
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
		details = "This function takes everything after the trigger and tried to define it",
		need_content = False
	),
	dict(
		name = "Whois",
		function = whois,
		description = "Gives a summary of a user, with everything he has\n"\
			"(does not include EXP and Currency, these are sepperate commands)",
		details = "This function takes one 1 optional argument\n"\
			"(1) Query string to search a user: name, mention, ID or None for the command caller",
		need_content = False
	),
	dict(
		name = "Prune messages",
		function = pruneMessages,
		description = "Deletes multiple messages in a channel.\n"\
			"By number or member\n"\
			"(It's highly recommended to set the requirement higher than Everyone)",
		details = "This function takes one 1 required argument\n"\
			"[1] Number or query string to search a user: name, mention or ID",
		need_content = False
	),
	dict(
		name = "Wikipedia search",
		function = searchWikipedia,
		description = "Let's you search through wikipedia.\n"\
			"Tryes to autocomplete your input (if possible)",
		details = "This function takes everything after the trigger and search for it",
		need_content = False
	),
	dict(
		name = "osu! | Player statistics",
		function = osuStats,
		description = "Returns a summary of a osu!player stats.",
		details = "This function takes 1 required argument\n"\
			"[1] A query string for the user: name or osu-ID\n"\
			"Extra Args: include '--ctb', '--taiko' or '--mania'\n"\
			"to change search mode\n"\
			"this arg will be filtered out of the search query",
		need_content = False
	),
	dict(
		name = "Assign role | Add",
		function = addAssignRole,
		description = "Add's a new entry for assign roles.\n"\
			"(It's highly recommended to set the requirement higher than Everyone)",
		details = "This function takes 2 required arguments\n"\
			"[1] A word as the role-trigger\n"\
			"[2] A query string for the role: name, mention or ID",
		need_content = False
	),
	dict(
		name = "Assign role | List",
		function = listAssignRole,
		description = "Lists all existing assign roles.",
		details = "This command does not take any arguments",
		need_content = False
	),
	dict(
		name = "Assign role | Remove",
		function = removeAssignRole,
		description = "Removes a assign roles.\n"\
			"(It's highly recommended to set the requirement higher than Everyone)",
		details = "This function takes 1 required argument\n"\
			"[1] The role-trigger",
		need_content = False
	),
	dict(
		name = "Assign role | Give/Take",
		function = assignRole,
		description = "Gives or takes a role from the user, based on the used preset role-trigger.\n"\
			"If user has the role, remove it, if not, add it",
		details = "This function takes 1 required argument\n"\
			"[1] The role-trigger",
		need_content = False
	),
	dict(
		name = "Level | Statistics",
		function = levelStatus,
		description = "Returns current level, exp and medals for a member.",
		details = "This function takes one 1 optional argument\n"\
			"(1) Query string to search a user: name, mention, ID or None for the command caller",
		need_content = False
	),
	dict(
		name = "Level | Leaderboard",
		function = levelLeaderboard,
		description = "Returns current level, exp and medals for a group of member.",
		details = "This function takes one 1 optional argument\n"\
			"(1) Number as the lengh for the list, max 15",
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
