from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

import re
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordcommandcontext import DiscordCommandContext
from Utils.regex import Osu as ReOsu

async def osuStats(cls:"PhaazebotDiscord", Command:DiscordCommand, CommandContext:DiscordCommandContext) -> dict:

	search_mode:str = "osu"
	if "--ctb" in CommandContext.parts:
		CommandContext.parts.remove("--ctb")
		search_mode = "ctb"
	elif "--taiko" in CommandContext.parts:
		CommandContext.parts.remove("--taiko")
		search_mode = "taiko"
	elif "--mania" in CommandContext.parts:
		CommandContext.parts.remove("--mania")
		search_mode = "mania"

	content:str = " ".join(CommandContext.parts)

	search_by:str = None
	is_id:bool = False
	search_by, is_id = extractUserInfo(content)

	# API request















	return {"content": "TODO"}


def extractUserInfo(search_str:str) -> tuple:
	Hit:re.Match = re.match(ReOsu.Userlink, search_str)
	if Hit:
		return Hit.group("id"), True

	return search_str, False
