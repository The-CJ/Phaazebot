from typing import Awaitable
from Utils.Classes.storeclasses import GlobalStorage

from .Processing.textonly import textOnly

REQUIRE_EVERYONE:int = 0
REQUIRE_SUB:int = 1
REQUIRE_VIP:int = 2
REQUIRE_REGULAR:int = 3
REQUIRE_MOD:int = 4
REQUIRE_OWNER:int = 5
REQUIRE_ADMIN:int = 6
REQUIRE_SYSTEM:int = 7

command_register:list = [
	dict(
		name = "Text dummy",
		function = textOnly,
		description = "A simple text dummy that returns a predefined text. It's the simplest thing you can imagine.\n"\
			"It requires a content, this content supports placeholder variables, like: [user-name] or [channel-name], etc...",
		required_arguments = [],
		optional_arguments = [],
		endless_arguemnts = True,
		need_content = True,
		allowes_content = True,
		example_calls = ["!myCommand", ">show_Something", "-text-dummy"],
		recommended_require = REQUIRE_EVERYONE,
		recommended_cooldown = 10,
	),
]

GlobalStorage.add("twitch_command_register", command_register)

def getTwitchCommandFunction(command_name:str) -> Awaitable:
	"""
	get the associated function to name, else handle it as a text only
	"""
	# should not happen
	if not command_name: return textOnly

	for cmd in command_register:
		if cmd["function"].__name__ == command_name: return cmd["function"]

	return textOnly
