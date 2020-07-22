from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Discord.utils import getDiscordGuildFromString
from Platforms.Web.Processing.Api.errors import apiNotAllowed, apiMissingData
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown

SEARCH_OPTIONS:List[str] = ["guild", "member", "role", "channel"]

async def apiDiscordSearch(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
	Default url: /api/discord/search
	"""
	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	if not PhaazeDiscord: return await apiNotAllowed(cls, WebRequest, msg="Discord module is not active")

	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	search:str = Data.getStr("search", "", len_max=128)
	term:str = Data.getStr("term", "", len_max=512)

	if search not in SEARCH_OPTIONS:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'search', allowed: " + ", ".join(SEARCH_OPTIONS))

	if not term:
		return await apiMissingData(cls, WebRequest, msg="invalid or missing 'term'")

	if search == "guild":
		return await searchGuild(cls, WebRequest, term)

async def searchGuild(cls:"WebIndex", WebRequest:WebRequestContent, search_term:str) -> Response:

	Searched:discord.Guild = getDiscordGuildFromString(cls.Web.BASE.Discord, search_term)
	if not Searched: return await apiDiscordGuildUnknown(cls, WebRequest)

	data:dict = {
		"name": str(Searched.name),
		"id": str(Searched.id),
		"owner_id": str(Searched.owner_id),
		"icon": Searched.icon,
		"banner": Searched.banner
	}

	return cls.response(
		text=json.dumps(
			dict( result=data, status=200 )
		),
		content_type="application/json",
		status=200
	)
