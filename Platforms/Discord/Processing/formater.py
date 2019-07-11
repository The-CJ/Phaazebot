from typing import Iterator
import re
from Utils.regex import Discord as ReDiscord
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordcommandcontext import DiscordCommandContext

async def formatVars(Command:DiscordCommand, CommandContext:DiscordCommandContext) -> str:

	format_str:str = Command.content

	format_str = format_str.replace("[user-name]", CommandContext.Message.author.name)
	format_str = format_str.replace("[user-mention]", CommandContext.Message.author.mention)
	format_str = format_str.replace("[channel-name]", CommandContext.Message.channel.name)
	format_str = format_str.replace("[channel-mention]", CommandContext.Message.channel.mention)
	format_str = format_str.replace("[server-name]", CommandContext.Message.guild.name)
	format_str = format_str.replace("[member-count]", str(CommandContext.Message.guild.member_count))
	format_str = format_str.replace("[uses]", str(Command.uses))

	VarHits:Iterator = re.finditer(ReDiscord.CommandVariableString, format_str)

	for Match in VarHits:
		name:str = Match.group("name")

		# check for and replace all $0 $4 $5 ...
		PositionMatch = re.match(r"\$(\d+)", name)
		if PositionMatch:
			rep:str = CommandContext.part(int(PositionMatch.group(1)))
			if not rep: rep = ""
			format_str = format_str.replace(Match.group(0), rep)


	return format_str
