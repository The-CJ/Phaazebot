from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

import discord
import requests
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordcommandcontext import DiscordCommandContext

URBANLINK:str = "https://api.urbandictionary.com/v0/define"

async def urbanDictionary(cls:"PhaazebotDiscord", Command:DiscordCommand, CommandContext:DiscordCommandContext) -> dict:

	search_term:str = " ".join([x for x in CommandContext.parts[1:]])
	if not search_term:
		return {"content": ":warning: You need at least one word to define"}

	try:
		res:dict = requests.get(URBANLINK, {"term": search_term}).json()
	except:
		return {"content": ":warning: A Error occurred during your request, try again later"}

	if not res.get("list", []):
		return {"content": f":x: Sorry, but Urban dictionary don't know what: `{search_term}` is"}

	top_item:dict = res["list"][0]

	top_definition:str = top_item.get("definition", "[N/A]")
	top_example:str = top_item.get("example", "[N/A]")
	top_word:str = top_item.get("word", "[N/A]")
	top_link:str = top_item.get("permalink", "[N/A]")

	more:int = len(res["list"][1:])

	Emb = discord.Embed(description=f":notebook_with_decorative_cover:\n{top_definition}")
	Emb.set_author(name=top_word, url=top_link)
	Emb.add_field(name=":book: Example", value=top_example)
	if more: Emb.set_footer(text=f"and {str(more)} other definitions")

	return {"embed": Emb}
