from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

import discord
from Utils.Classes.discordquote import DiscordQuote
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordcommandcontext import DiscordCommandContext
from Platforms.Discord.utils import getDiscordServerQuotes

async def showQuote(cls:"PhaazebotDiscord", Command:DiscordCommand, CommandContext:DiscordCommandContext) -> dict:

	specific_id:str = CommandContext.part(1)
	if specific_id:
		if not specific_id.isdigit():
			specific_id = ""

	if specific_id:
		random:bool = False
	else:
		random:bool = True

	quote:list = await getDiscordServerQuotes(cls, Command.server_id, quote_id=specific_id, random=random, limit=1)

	if not quote and not specific_id:
		return {"content": ":grey_exclamation: This server don't has any Quotes"}
	elif not quote and specific_id:
		return {"content": f":warning: No quote found with id {specific_id} on this server"}
	else:
		Quote:DiscordQuote = quote[0]

		Emb = discord.Embed(description=str(Quote.content))
		Emb.set_footer(text=f"ID: {str(Quote.quote_id)}")
		return {"embed": Emb}
