from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Discord.db import getDiscordUsersMedals, getDiscordUsersMedalAmount
from Platforms.Web.Processing.Api.errors import apiMissingData
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown

DEFAULT_LIMIT:int = 50
MAX_LIMIT:int = 100

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
	name_contains:str = Data.getStr("name_contains", "", len_max=512)
	medal_id:str = Data.getStr("medal_id", "", must_be_digit=True)
	limit:int = Data.getInt("limit", DEFAULT_LIMIT, min_x=1, max_x=MAX_LIMIT)
	offset:int = Data.getInt("offset", 0, min_x=0)

	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	# get medals
	res_medals:list = await getDiscordUsersMedals(PhaazeDiscord, guild_id, member_id=member_id, medal_id=medal_id, limit=limit, offset=offset, name=name, name_contains=name_contains)

	return cls.response(
		text=json.dumps( dict(
			result=[ Medal.toJSON() for Medal in res_medals ],
			limit=limit,
			offset=offset,
			total=(await getDiscordUsersMedalAmount(PhaazeDiscord, guild_id)),
			status=200)
		),
		content_type="application/json",
		status=200
	)
