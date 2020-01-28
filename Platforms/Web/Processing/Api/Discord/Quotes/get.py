from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Discord.utils import getDiscordServerQuotes
from Utils.Classes.undefined import UNDEFINED
from Platforms.Web.Processing.Api.errors import apiMissingData
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown

DEFAULT_LIMIT:int = 50
MAX_LIMIT:int = 100

async def apiDiscordQuotesGet(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/quotes/get
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	quote_id:int = Data.getInt("quote_id", UNDEFINED, min_x=1)
	limit:int = Data.getInt("limit", DEFAULT_LIMIT, min_x=1, max_x=MAX_LIMIT)
	offset:int = Data.getInt("offset", 0, min_x=0)

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	# get quotes
	res_quotes:list = await getDiscordServerQuotes(PhaazeDiscord, guild_id=guild_id, quote_id=quote_id, limit=limit, offset=offset)

	return cls.response(
		text=json.dumps( dict(
			result=[ Quote.toJSON() for Quote in res_quotes ],
			total=len(res_quotes),
			status=200)
		),
		content_type="application/json",
		status=200
	)
