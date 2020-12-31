from typing import Callable, List
# noinspection PyPep8Naming
import Platforms.Discord.const as DiscordConst
from Utils.Classes.storeclasses import GlobalStorage

from Platforms.Discord.Processing.textonly import textOnly
from Platforms.Discord.Processing.listcommands import listCommands
from Platforms.Discord.Processing.showquote import showQuote
from Platforms.Discord.Processing.addquote import addQuote
from Platforms.Discord.Processing.removequote import removeQuote
from Platforms.Discord.Processing.randomchoice import randomChoice
from Platforms.Discord.Processing.urbandictionary import urbanDictionary
from Platforms.Discord.Processing.whois import whois
from Platforms.Discord.Processing.prunemessages import pruneMessages
from Platforms.Discord.Processing.wikipedia import searchWikipedia
from Platforms.Discord.Processing.osustatus import osuStats
from Platforms.Discord.Processing.listassignrole import listAssignRole
from Platforms.Discord.Processing.addassignrole import addAssignRole
from Platforms.Discord.Processing.removeassignrole import removeAssignRole
from Platforms.Discord.Processing.assignrole import assignRole
from Platforms.Discord.Processing.levelstatus import levelStatus
from Platforms.Discord.Processing.levelleaderboard import levelLeaderboard

command_register:List[dict] = [
	dict(
		name="Text dummy",
		function=textOnly,
		description="A simple text dummy that returns a predefined text. It's the simplest thing you can imagine.\n"
			"It requires a content, this content supports placeholder variables, like: [user-name], [channel-name] or [member-count], etc...",
		required_arguments=[],
		optional_arguments=[],
		endless_arguemnts=True,
		need_content=True,
		allowes_content=True,
		example_calls=[
			"!myCommand",
			">do_Something",
			"-text-dummy",
		],
		recommended_require=DiscordConst.REQUIRE_EVERYONE,
		recommended_cooldown=10,
	),
	dict(
		name="Commands | List",
		function=listCommands,
		description="List all* commands a server has, also provides a link to the public command website\n"
			"* It only shows the first 20 commands, after that it only says there are more. Else it would be to spamy",
		required_arguments=[],
		optional_arguments=[],
		endless_arguemnts=False,
		need_content=False,
		allowes_content=False,
		example_calls=[
			"!listcmd",
			">cmd",
			"show_me_commands",
		],
		recommended_require=DiscordConst.REQUIRE_EVERYONE,
		recommended_cooldown=20,
	),
	dict(
		name="Quote | Show",
		function=showQuote,
		description="If not defined otherwise, it returns a random quote from this server",
		required_arguments=[],
		optional_arguments=[
			"(1) ID of requested Quote"
		],
		endless_arguemnts=False,
		need_content=False,
		allowes_content=False,
		example_calls=[
			"!quote",
			">quote 8",
			"!quote 221",
		],
		recommended_require=DiscordConst.REQUIRE_EVERYONE,
		recommended_cooldown=30,
	),
	dict(
		name="Quote | Add",
		function=addQuote,
		description="Adds a new quote to the server quote list. Very useful if you don't wanna open your web browser and just add it in discord.",
		required_arguments=[],
		optional_arguments=[],
		endless_arguemnts=True,
		need_content=False,
		allowes_content=False,
		example_calls=[
			"!newquote 'This is my new Quote'",
			">AddQuote Something something -Strange Dude",
			"!remember \"Some funny quote i guess, or whatever you wanna quote.\" -Dev",
		],
		recommended_require=DiscordConst.REQUIRE_REGULAR,
		recommended_cooldown=30,
	),
	dict(
		name="Quote | Remove",
		function=removeQuote,
		description="Removes a quote from the server quote list. Do be sure, its recommended to remove them via web.",
		required_arguments=[
			"[1] The Quote ID to delete."
		],
		optional_arguments=[],
		endless_arguemnts=False,
		need_content=False,
		allowes_content=False,
		example_calls=[
			"!removequote 6",
			">delete 51",
			"!Quote-rem 81",
		],
		recommended_require=DiscordConst.REQUIRE_MOD,
		recommended_cooldown=30,
	),
	dict(
		name="Random choice",
		function=randomChoice,
		description="Takes all arguments after the command-trigger , separated by ;\n"
			"Gives back one of the splatted content",
		required_arguments=[],
		optional_arguments=[],
		endless_arguemnts=True,
		need_content=False,
		allowes_content=False,
		example_calls=[
			"!rand option 1;option 2",
			">num 1;2;3;4;5;6",
			"!random This is a long option;This one to, but is also just one option",
		],
		recommended_require=DiscordConst.REQUIRE_EVERYONE,
		recommended_cooldown=30,
	),
	dict(
		name="Urban define",
		function=urbanDictionary,
		description="Uses UrbanDictionary to get a definition for your input",
		required_arguments=[],
		optional_arguments=[],
		endless_arguemnts=True,
		need_content=False,
		allowes_content=False,
		example_calls=[
			"!define Orange",
			">what_is Sleeping",
			"!urban The goal of life",
		],
		recommended_require=DiscordConst.REQUIRE_EVERYONE,
		recommended_cooldown=30,
	),
	dict(
		name="Whois",
		function=whois,
		description="Gives a summary of a user, with everything he has\n"
			"(does not include EXP and Currency, these are separate commands)",
		required_arguments=[],
		optional_arguments=[
			"(1) Query string to search a user: name, mention, ID or None for the command caller"
		],
		endless_arguemnts=False,
		need_content=False,
		allowes_content=False,
		example_calls=[
			"!whois",
			">inspect SomeUser#5482",
			"!show 117746512380952582",
		],
		recommended_require=DiscordConst.REQUIRE_EVERYONE,
		recommended_cooldown=30,
	),
	dict(
		name="Prune messages",
		function=pruneMessages,
		description="Deletes multiple messages in a channel.\n"
			"Very useful if you wanna cleanup some messages that are not fitting in your server,\n"
			"or remove any trace of members that broke rules and got banned",
		required_arguments=[
			"[1] Number of messages or query string to search a user: name, mention or ID"
		],
		optional_arguments=[],
		endless_arguemnts=False,
		need_content=False,
		allowes_content=False,
		example_calls=[
			"!clean 200",
			">prune BadUser#2314",
			"!trash 227503088649371658",
		],
		recommended_require=DiscordConst.REQUIRE_MOD,
		recommended_cooldown=30,
	),
	dict(
		name="Wikipedia search",
		function=searchWikipedia,
		description="Let's you search through wikipedia.\n"
			"Tries to autocomplete your input (if possible) and gives you a quick summary",
		required_arguments=[],
		optional_arguments=[],
		endless_arguemnts=False,
		need_content=False,
		allowes_content=False,
		example_calls=[
			"!wiki Carbon dioxide",
			">wikipedia Earth",
			"-www internet",
		],
		recommended_require=DiscordConst.REQUIRE_EVERYONE,
		recommended_cooldown=60,
	),
	dict(
		name="osu! | Player statistics",
		function=osuStats,
		description="Returns a summary of a osu!player stats.\n"
			"The search mode can be changed, if you want to look up, ctb or taiko, or whatever",
		required_arguments=[
			"[1] A query string for the user: name or osu-ID"
		],
		optional_arguments=[
			"Change search mode: '--ctb', '--taiko', '--mania' (Anywhere in the command, will be filtered out)"
		],
		endless_arguemnts=False,
		need_content=False,
		allowes_content=False,
		example_calls=[
			"!osu-stats playername",
			">osu another --ctb",
			"-o 789752 --mania",
		],
		recommended_require=DiscordConst.REQUIRE_EVERYONE,
		recommended_cooldown=30,
	),
	dict(
		name="Assign role | Add",
		function=addAssignRole,
		description="Adds a new entry for assign roles. However doing this via a command in discord can be heavy, its recommended to do this via web.",
		required_arguments=[
			"[1] A word as the role-trigger",
			"[2] A query string for the role: name, mention or ID"
		],
		optional_arguments=[],
		endless_arguemnts=False,
		need_content=False,
		allowes_content=False,
		example_calls=[
			"!add-role csgo @Counterstrike",
			">ar minecraft 58694231456489579",
			"-assign-add notify @stream alert role",
		],
		recommended_require=DiscordConst.REQUIRE_MOD,
		recommended_cooldown=30,
	),
	dict(
		name="Assign role | List",
		function=listAssignRole,
		description="Lists all existing assign roles.",
		required_arguments=[],
		optional_arguments=[],
		endless_arguemnts=False,
		need_content=False,
		allowes_content=False,
		example_calls=[
			"!listroles",
			">assign_list",
			"-arl",
		],
		recommended_require=DiscordConst.REQUIRE_EVERYONE,
		recommended_cooldown=30,
	),
	dict(
		name="Assign role | Remove",
		function=removeAssignRole,
		description="Removes a assign roles. However doing this via a command in discord can be heavy, its recommended to do this via web.",
		required_arguments=[
			"[1] The assign-role trigger"
		],
		optional_arguments=[],
		endless_arguemnts=False,
		need_content=False,
		allowes_content=False,
		example_calls=[
			"!remove-assign csgo",
			">assign_del minecraft",
			"-ard notify",
		],
		recommended_require=DiscordConst.REQUIRE_MOD,
		recommended_cooldown=30,
	),
	dict(
		name="Assign role | Give/Take",
		function=assignRole,
		description="Gives or takes a role from the user, based on the used preset role-trigger.\n"
			"If user has the role: remove it, if not: add it",
		required_arguments=[
			"[1] The assign-role trigger"
		],
		optional_arguments=[],
		endless_arguemnts=False,
		need_content=False,
		allowes_content=False,
		example_calls=[
			"!assign csgo",
			">give-role minecraft",
			"-a notify",
		],
		recommended_require=DiscordConst.REQUIRE_EVERYONE,
		recommended_cooldown=30,
	),
	dict(
		name="Level | Statistics",
		function=levelStatus,
		description="Returns a summary of the current level, exp and medals for a member.",
		required_arguments=[],
		optional_arguments=[
			"(1) Query string to search a user: name, mention, ID or None for the command caller"
		],
		endless_arguemnts=False,
		need_content=False,
		allowes_content=False,
		example_calls=[
			"!level",
			">lvl @AnotherUser",
			"-stats 45748432469745648662",
		],
		recommended_require=DiscordConst.REQUIRE_EVERYONE,
		recommended_cooldown=30,
	),
	dict(
		name="Level | Leaderboard",
		function=levelLeaderboard,
		description="Returns current level, exp and medals for a group of member.",
		required_arguments=[],
		optional_arguments=[
			"(1) Number for the length for the list, max 15"
		],
		endless_arguemnts=False,
		need_content=False,
		allowes_content=False,
		example_calls=[
			"!leaderboard",
			">board 3",
			"-b 13",
		],
		recommended_require=DiscordConst.REQUIRE_EVERYONE,
		recommended_cooldown=30,
	),
]

GlobalStorage.add("discord_command_register", command_register)

def getDiscordCommandFunction(command_name: str) -> Callable:
	"""
	get the associated function to name, else handle it as a text only
	"""
	# should not happen
	if not command_name: return textOnly

	for cmd in command_register:
		if cmd["function"].__name__ == command_name: return cmd["function"]

	return textOnly
