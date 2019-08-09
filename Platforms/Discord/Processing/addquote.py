from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

import discord
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordcommandcontext import DiscordCommandContext

async def addQuote(cls:"PhaazebotDiscord", Command:DiscordCommand, CommandContext:DiscordCommandContext) -> dict:

	res:list = cls.BASE.PhaazeDB.query("""
		SELECT COUNT(*) AS c
		FROM discord_quote
		WHERE discord_quote.guild_id = %s""",
		(Command.server_id,)
	)

	if res[0]["c"] >= cls.BASE.Limit.DISCORD_QUOTES_AMOUNT:
		return {"content": ":no_entry_sign: This server hit the quote limit, please remove some first."}


	new_quote:str = CommandContext.parts[1:]
