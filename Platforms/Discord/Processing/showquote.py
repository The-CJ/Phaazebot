from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

import discord
from Utils.Classes.discordquote import DiscordQuote
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordcommandcontext import DiscordCommandContext
from Platforms.Discord.db import getDiscordServerQuotes

async def showQuote(cls:"PhaazebotDiscord", Command:DiscordCommand, CommandContext:DiscordCommandContext) -> dict:

	specific_id:str = CommandContext.part(1)
	if specific_id:
		if not specific_id.isdigit():
			specific_id = ""

	search:dict = dict()
	search["guild_id"] = Command.server_id
	search["quote_id"] = specific_id
	search["limit"] = 1

	if not specific_id:
		search["order_str"] = "ORDER BY RAND()"

	quote:list = await getDiscordServerQuotes(cls,**search)

	if not quote and not specific_id:
		return {"content": ":grey_exclamation: This server don't has any Quotes"}
	elif not quote and specific_id:
		return {"content": f":warning: No quote found with id {specific_id} on this server"}
	else:
		Quote:DiscordQuote = quote[0]

		Emb = discord.Embed(description=str(Quote.content))
		Emb.set_footer(text=f"ID: {str(Quote.quote_id)}")
		return {"embed": Emb}
