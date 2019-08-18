from typing import TYPE_CHECKING
if TYPE_CHECKING or 1:
	from Platforms.Discord.main_discord import PhaazebotDiscord

import re
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordcommandcontext import DiscordCommandContext
from Utils.regex import Osu as ReOsu
from Platforms.Osu.api import getOsuUser

async def osuStats(cls:"PhaazebotDiscord", Command:DiscordCommand, CommandContext:DiscordCommandContext) -> dict:

	search_mode:str = "0"
	if "--taiko" in CommandContext.parts:
		CommandContext.parts.remove("--taiko")
		search_mode = "1"
	elif "--ctb" in CommandContext.parts:
		CommandContext.parts.remove("--ctb")
		search_mode = "2"
	elif "--mania" in CommandContext.parts:
		CommandContext.parts.remove("--mania")
		search_mode = "3"

	content:str = " ".join(CommandContext.parts)

	search_by:str = None
	is_id:bool = False
	search_by, is_id = extractUserInfo(content)

	# API request
	result:list = await getOsuUser(cls.BASE, search=search_by, mode=search_mode, is_id=is_id)














	return {"content": "TODO"}


def extractUserInfo(search_str:str) -> tuple:
	Hit:re.Match = re.match(ReOsu.Userlink, search_str)
	if Hit:
		return Hit.group("id"), True

	return search_str, False
