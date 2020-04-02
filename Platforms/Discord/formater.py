from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from .main_discord import PhaazebotDiscord

import re
import discord
from typing import Iterator
from Utils.regex import Discord as ReDiscord
from Utils.Classes.discordcommandcontext import DiscordCommandContext
from Platforms.Discord.utils import getDiscordChannelFromString

async def responseFormater(cls:"PhaazebotDiscord", content:str, *x:list, **kwargs:dict) -> str:
	"""
	This new formater is support to ensure all formatings with all known regex
	means all [key] fields, if there are provided,
	but also special regex like <#name#>

	Info source keywords:
	-------------
	* DiscordGuild `discord.Guild` : (Default: None) [ Enables (A) ]
	* CommandContext `DiscordCommandContext` : (Default: None) [ Enables (B) ]

	Optional keywords:
	------------------
	* enable_special `bool` (A) : (Default: False) [Replaces <#name#> or <#!id!#>]
	* enable_positions `bool` (B) : (Default: False) [Replaces $1, $6, etc.]
	* var_dict `dict` : (Default: None) [Replaces all keys with dict value]
	* VarRegex `re.Pattern` : (Default: CommandVariableString)
	"""

	DiscordGuild:discord.Guild = kwargs.get("DiscordGuild", None)
	CommandContext:DiscordCommandContext = kwargs.get("CommandContext", None)

	enable_special:bool = bool( kwargs.get("enable_special", False) )
	enable_positions:bool = bool( kwargs.get("enable_positions", False) )
	var_dict:dict = kwargs.get("var_dict", {})
	VarRegex:"re.Pattern" = kwargs.get("VarRegex", ReDiscord.CommandVariableString)
	CommandContext:DiscordCommandContext = kwargs.get("CommandContext", None)

	# replaces [key1] [key2] with values from a same name dict
	if var_dict:
		VarHits:Iterator = re.finditer(VarRegex, content)
		for VarMatch in VarHits:
			key:str = VarMatch.group("name")

			if key in var_dict:
				content = content.replace( VarMatch.group(0), var_dict[key] )

	# replaces $1 $5 $7 etc... at Positions
	if enable_positions and CommandContext:
		PositionMatch:Iterator = re.finditer(ReDiscord.CommandPosString, content)
		for PosMatch in PositionMatch:
			replacement:str = CommandContext.part(int(PosMatch.group("pos")))
			if not replacement: replacement = ""
			content = content.replace(PosMatch.group(0), replacement)

	# replaces <#name#> and <#!id!#> with the correct channel mention
	if enable_special and DiscordGuild:
		ChannelNameIter:Iterator = re.finditer(ReDiscord.SpecialStringChannelName, content)
		ChannelIDIter:Iterator = re.finditer(ReDiscord.SpecialStringChannelID, content)

		found:list = []

		for NameMatch in ChannelNameIter: found.append(NameMatch)
		for IDMatch in ChannelIDIter: found.append(IDMatch)

		if found:
			for Hit in found:
				ChannelToMention:discord.abc.GuildChannel = getDiscordChannelFromString(cls, DiscordGuild, Hit.group(1))
				if ChannelToMention:
					content = content.replace( Hit.group(0), ChannelToMention.mention )
				else:
					content = content.replace( Hit.group(0), "(unknown)" )

	return content
