from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

import random
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordcommandcontext import DiscordCommandContext

async def randomChoice(cls:"PhaazebotDiscord", Command:DiscordCommand, CommandContext:DiscordCommandContext) -> dict:

	if len(CommandContext.parts) == 1:
		return {"content": ":warning: Missing arguments, at least 2 options separated by \";\" are needed"}

	arg_str:str = " ".join(s for s in CommandContext.parts[1:])
	pool:list = arg_str.split(";")

	for item in pool:
		if not item:
			pool.remove(item)
			continue

	winner:str = random.choice(pool)

	# remove all unwanted stuff
	winner = winner.replace("`", "")
	winner = winner.replace("@everyone", "")
	winner = winner.replace("**", "")

	resp:str = f"And the winner is...\n\n:game_die:- **{winner}** -:8ball:"

	return {"content": resp}
