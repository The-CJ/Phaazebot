from typing import Iterator
import re
from Utils.regex import Discord as ReDiscord
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordcommandcontext import DiscordCommandContext

async def formatVars(Command:DiscordCommand, CommandContext:DiscordCommandContext) -> str:

	format_str:str = Command.content

	replace_index:dict = {
		"user-name": CommandContext.Message.author.name,
		"user-mention": CommandContext.Message.author.mention,
		"channel-name": CommandContext.Message.channel.name,
		"channel-mention": CommandContext.Message.channel.mention,
		"server-name": CommandContext.Message.guild.name,
		"member-count": str(CommandContext.Message.guild.member_count),
		"uses": str(Command.uses)
	}

	# check for and replace all [varname] [varname2] ...
	VarHits:Iterator = re.finditer(ReDiscord.CommandVariableString, format_str)
	for VarMatch in VarHits:
		name:str = VarMatch.group("name")

		if name in replace_index:
			format_str = format_str.replace(VarMatch.group(0), replace_index[name])

	# check for and replace all $0 $4 $5 ...
	PositionMatch:Iterator = re.finditer(ReDiscord.CommandPosString, format_str)
	for PosMatch in PositionMatch:
		rep:str = CommandContext.part(int(PosMatch.group("pos")))
		if not rep: rep = ""
		format_str = format_str.replace(PosMatch.group(0), rep)

	return format_str
