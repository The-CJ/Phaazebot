from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

from Utils.Classes.discordquote import DiscordQuote
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordcommandcontext import DiscordCommandContext
from Platforms.Discord.utils import getDiscordServerQuotes

async def removeQuote(cls:"PhaazebotDiscord", Command:DiscordCommand, CommandContext:DiscordCommandContext) -> dict:

	specific_id:str = CommandContext.part(1)
	if specific_id:
		if not specific_id.isdigit():
			specific_id = ""

	if not specific_id:
		return {"content": ":warning: You need to define a numeric quote ID to remove."}

	quote:list = await getDiscordServerQuotes(cls, Command.server_id, quote_id=specific_id)

	if not quote:
		return {"content": f":warning: There is no Quote with ID #{specific_id}"}

	DQuote:DiscordQuote = quote[0]

	cls.BASE.PhaazeDB.deleteQuery("""
		DELETE FROM `discord_quote`
		WHERE `discord_quote`.`guild_id` = %s
		AND `discord_quote`.`id` = %s""",
		( str(DQuote.guild_id), str(DQuote.quote_id) )
	)

	return {"content": f":white_check_mark: Quote #{specific_id} removed"}
