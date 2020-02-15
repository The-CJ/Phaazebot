from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

import discord
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordcommandcontext import DiscordCommandContext

async def addQuote(cls:"PhaazebotDiscord", Command:DiscordCommand, CommandContext:DiscordCommandContext) -> dict:

	new_quote = " ".join( CommandContext.parts[1:] )

	if not new_quote:
		return {"content": ":warning: You need to define a quote content to add."}

	res:list = cls.BASE.PhaazeDB.query("""
		SELECT COUNT(*) AS `I`
		FROM `discord_quote`
		WHERE `discord_quote`.`guild_id` = %s""",
		(Command.server_id,)
	)

	if res[0]["I"] >= cls.BASE.Limit.DISCORD_QUOTES_AMOUNT:
		return {"content": ":no_entry_sign: This server hit the quote limit, please remove some first."}

	new_quote_id:int = cls.BASE.PhaazeDB.insertQuery(
		table = "discord_quote",
		content = dict(
			guild_id = str(Command.server_id),
			content = new_quote,
		)
	)

	Emb = discord.Embed(description=new_quote, color=0x11EE11)
	Emb.set_footer(text=f'ID: {new_quote_id}')

	return {"content": ":white_check_mark: Quote added", "embed": Emb}
