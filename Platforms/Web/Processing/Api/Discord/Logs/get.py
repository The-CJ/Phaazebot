from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.discordlog import DiscordLog
from Platforms.Discord.db import getDiscordServerLogs, getDiscordServerLogAmount
from Platforms.Web.Processing.Api.errors import apiMissingData
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown

DEFAULT_LIMIT:int = 50
MAX_LIMIT:int = 100

async def apiDiscordLogsGet(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
	Default url: /api/discord/logs/get
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	log_id:str = Data.getStr("log_id", "", must_be_digit=True)
	event_value:int = Data.getInt("event_value", 0, min_x=0)
	content_contains:str = Data.getStr("content_contains", "", len_max=512)
	date_from:str = Data.getStr("date_from", "")
	date_to:str = Data.getStr("date_to", "")
	limit:int = Data.getInt("limit", DEFAULT_LIMIT, min_x=1, max_x=MAX_LIMIT)
	offset:int = Data.getInt("offset", 0, min_x=0)

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	logs:List[DiscordLog] = await getDiscordServerLogs(PhaazeDiscord, guild_id=guild_id, log_id=log_id, event_value=event_value, content_contains=content_contains, date_from=date_from, date_to=date_to, limit=limit, offset=offset)

	return cls.response(
		text=json.dumps( dict(
			result=[ Log.toJSON() for Log in logs ],
			total=await getDiscordServerLogAmount(PhaazeDiscord, guild_id),
			limit=limit,
			offset=offset,
			status=200)
		),
		content_type="application/json",
		status=200
	)
