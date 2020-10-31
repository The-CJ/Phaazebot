from typing import Awaitable
from Utils.Classes.storeclasses import GlobalStorage
import Platforms.Twitch.const as TwitchConst

from .Processing.textonly import textOnly

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
		recommended_require = TwitchConst.REQUIRE_EVERYONE,
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
