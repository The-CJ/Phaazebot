from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

import requests
import discord
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordcommandcontext import DiscordCommandContext
from Utils.stringutils import numberToHugeLetter

PATH_SEARCH:str = "https://en.wikipedia.org/w/api.php"
PATH_SUMMARY:str = "https://en.wikipedia.org/api/rest_v1/page/summary/"

async def searchWikipedia(cls:"PhaazebotDiscord", Command:DiscordCommand, CommandContext:DiscordCommandContext) -> dict:

	search:str = " ".join([x for x in CommandContext.parts[1:]])

	if not search:
		return {"content": ":warning: You need to define something you wanna search for."}

	try:
		res:list = requests.get(PATH_SEARCH, {"action": "opensearch", "limit":"7", "search":search}).json()
	except:
		return {"content": ":warning: Could not connect to Wikipedia, try later again."}

	res:list = removeRefereTo(res)

	# res = ['<search>', [<found titles>], [<found quick-desc>], [<found links>]]
	if not res[1]:
		return {"content": f":x: Wikipedia could not found anything for `{res[0]}`."}

	# if <search> is in <found titles> return that one
	if res[0].lower() in [title.lower() for title in res[1]]:
		return await getSummary(cls, Command, CommandContext, res[0])

	else:
		return await autocomplete(cls, Command, CommandContext, res[1])

async def autocomplete(cls:"PhaazebotDiscord", Command:DiscordCommand, CommandContext:DiscordCommandContext, titles:list) -> dict:
	ask_text:list = list()
	title_number:int = 0
	for title in titles:
		title_number += 1
		ask_text.append( f"{numberToHugeLetter(title_number)} {title}" )
	ask_text.append( "Please type only the number you wanna search." )

	ask_text:str = "\n".join(ask_text)
	Emb:discord.Embed = discord.Embed(title=":grey_exclamation: There are multiple results. Please choose", description=ask_text)
	Emb.set_footer(text="Provided by Wikipedia", icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Wikipedia-logo-v2.svg/2000px-Wikipedia-logo-v2.svg.png")

	await CommandContext.Message.channel.send(embed=Emb)

	def check(Message:discord.Message):
		if Message.channel.id == CommandContext.Message.channel.id:
			if Message.author.id == CommandContext.Message.author.id:
				return True
		return False

	try:
		Res:discord.Message = await cls.wait_for("message", check=check, timeout=30)
	except:
		Res:discord.Message = None

	if (not Res) or (not Res.content.isdigit()):
		return {"content": ":warning: Please only enter a number... Try later again"}

	user_input:int = int(Res.content)
	if not (0 < user_input <= len(title)):
		return {"content": f":warning: Please only enter a number between 1 - {str(len(title))}... Try later again"}

	search_title:str = titles[ user_input-1 ]

	return await getSummary(cls, Command, CommandContext, search_title)

async def getSummary(cls:"PhaazebotDiscord", Command:DiscordCommand, CommandContext:DiscordCommandContext, title:str) -> dict:

	try:
		res:dict = requests.get(PATH_SUMMARY+title).json()
	except:
		return {"content": ":warning: something went wrong... try later again."}

	emb_title:str = res.get("title", None)
	emb_content:str = res.get("extract", None)
	emb_description:str = res.get("description", None)
	emb_url:str = res.get("content_urls", dict()).get('desktop', dict()).get('page', '')
	emb_thumbnail:str = res.get('thumbnail', dict()).get('source', '')

	Emb:discord.Embed = discord.Embed(title=emb_description, description=emb_content)
	Emb.set_author(name=emb_title, url=emb_url)
	Emb.set_thumbnail(url=emb_thumbnail)
	Emb.set_footer(text="Provided by Wikipedia", icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Wikipedia-logo-v2.svg/2000px-Wikipedia-logo-v2.svg.png")

	return {"embed": Emb}

def removeRefereTo(api_result:list) -> list:
	try:
		# res = ['<search>', [<found titles>], [<found quick-desc>], [<found links>]]
		first_description:str = api_result[2][0].lower()
		if not first_description or first_description.endswith(":"):
			# a thing not having a description means its a "refere to:" page, ignore these and remove
			api_result[1].pop(0)
			api_result[2].pop(0)
	except:	pass
	finally: return api_result
