from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

import discord
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordcommandcontext import DiscordCommandContext

async def addQuote(cls:"PhaazebotDiscord", Command:DiscordCommand, CommandContext:DiscordCommandContext) -> dict:

	new_quote:str = CommandContext.Message.content[(len(CommandContext.parts[0])):]

	if not new_quote:
		return {"content": ":warning: You need to define a quote content to add."}

	res:list = cls.BASE.PhaazeDB.query("""
		SELECT COUNT(*) AS c
		FROM discord_quote
		WHERE discord_quote.guild_id = %s""",
		(Command.server_id,)
	)

	if res[0]["c"] >= cls.BASE.Limit.DISCORD_QUOTES_AMOUNT:
		return {"content": ":no_entry_sign: This server hit the quote limit, please remove some first."}

	res:list = cls.BASE.PhaazeDB.query("""
		INSERT INTO discord_quote
		(guild_id, content)
		VALUES (%s, %s)""",
		(Command.server_id, new_quote)
	)

	new_quote_id:int = 0
	if res:
		new_quote_id = res[0]

	Emb = discord.Embed(description=new_quote, color=0x11EE11)
	Emb.set_footer(text=f'ID: {new_quote_id}')

	return {"content": ":white_check_mark: Quote added", "embed": Emb}
