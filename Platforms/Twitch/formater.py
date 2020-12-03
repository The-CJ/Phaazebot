from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Twitch.main_twitch import PhaazebotTwitch

import re
from typing import Iterator
from Utils.regex import Twitch as ReTwitch
from Utils.Classes.twitchcommandcontext import TwitchCommandContext

async def responseFormater(cls:"PhaazebotTwitch", content:str, *x:list, **kwargs:dict) -> str:
	"""
	This formater is support to ensure all formatings with all known regex
	means all [key] fields, if there are provided.

	Info source keywords:
	-------------
	* CommandContext `TwitchCommandContext` : (Default: None) [ Enables (A) ]

	Optional keywords:
	------------------
	* enable_positions `bool` (A) : (Default: False) [Replaces $1, $6, etc.]
	* var_dict `dict` : (Default: None) [Replaces all keys with dict value]
	* VarRegex `re.Pattern` : (Default: CommandVariableString)
	"""

	CommandContext:TwitchCommandContext = kwargs.get("CommandContext", None)

	enable_positions:bool = bool( kwargs.get("enable_positions", False) )
	var_dict:dict = kwargs.get("var_dict", {})
	VarRegex:"re.Pattern" = kwargs.get("VarRegex", ReTwitch.CommandVariableString)
	CommandContext:TwitchCommandContext = kwargs.get("CommandContext", None)

	# replaces [key1] [key2] with values from a same name dict
	if var_dict:
		VarHits:Iterator = re.finditer(VarRegex, content)
		for VarMatch in VarHits:
			key:str = VarMatch.group("name")

			if key in var_dict:
				content = content.replace( VarMatch.group(0), var_dict[key] )

	# replaces $1 $5 $7 etc... at Positions
	if enable_positions and CommandContext:
		PositionMatch:Iterator = re.finditer(ReTwitch.CommandPosString, content)
		for PosMatch in PositionMatch:
			replacement:str = CommandContext.part(int(PosMatch.group("pos")))
			if not replacement: replacement = ""
			content = content.replace(PosMatch.group(0), replacement)

	return content
