from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Web.Processing.Api.errors import apiMissingData
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown

async def apiDiscordLevelsMedalsGet(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/levels/medals/get
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	member_id:str = Data.getStr("member_id", "", must_be_digit=True)
	name:str = Data.getStr("name", "", len_max=512)
	medal_id:str = Data.getStr("medal_id", "", must_be_digit=True)

	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	if not member_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'member_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	# get medals
	# res_medals:list = await getDiscordUsersMedals(PhaazeDiscord)
