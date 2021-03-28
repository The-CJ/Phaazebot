from typing import TYPE_CHECKING, List, Dict, Any
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.main_web import PhaazebotWeb

import json
import discord
from aiohttp.web import Response
from Utils.Classes.storagetransformer import StorageTransformer
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.discordlog import DiscordLog
from Utils.Classes.undefined import UNDEFINED
from Platforms.Discord.db import getDiscordServerLogs
from Platforms.Web.Processing.Api.errors import apiMissingData
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown

DEFAULT_LIMIT:int = 50
MAX_LIMIT:int = 100

async def apiDiscordLogsGet(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/logs/get
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	Search:StorageTransformer = StorageTransformer()
	Search["guild_id"] = Data.getStr("guild_id", UNDEFINED, must_be_digit=True)
	Search["log_id"] = Data.getStr("log_id", UNDEFINED, must_be_digit=True)
	Search["event_value"] = Data.getInt("event_value", UNDEFINED, min_x=1)
	Search["content_contains"] = Data.getStr("content_contains", "", len_min=1, len_max=512)
	Search["date_from"] = Data.getStr("date_from", None, len_min=1, len_max=64)
	Search["date_to"] = Data.getStr("date_to", None, len_min=1, len_max=64)
	Search["created_at_between"] = (Search["date_from"], Search["date_to"])
	Search["limit"] = Data.getInt("limit", DEFAULT_LIMIT, min_x=1, max_x=MAX_LIMIT)
	Search["offset"] = Data.getInt("offset", 0, min_x=0)

	# checks
	if not Search["guild_id"]:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(Search["guild_id"]))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	log_res:List[DiscordLog] = await getDiscordServerLogs(PhaazeDiscord, **Search.getAllTransform())

	result:Dict[str, Any] = dict(
		result=[Log.toJSON() for Log in log_res],
		total=await getDiscordServerLogs(PhaazeDiscord, count_mode=True, **Search.getAllTransform()),
		limit=Search["limit"],
		offset=Search["offset"],
		status=200
	)

	return cls.response(
		text=json.dumps(result),
		content_type="application/json",
		status=200
	)
