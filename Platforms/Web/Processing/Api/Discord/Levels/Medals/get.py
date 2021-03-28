from typing import TYPE_CHECKING, Dict, Any
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response
from Utils.Classes.storagetransformer import StorageTransformer
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.undefined import UNDEFINED
from Platforms.Discord.db import getDiscordUsersMedals
from Platforms.Web.Processing.Api.errors import apiMissingData
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown

DEFAULT_LIMIT:int = 50
MAX_LIMIT:int = 100

async def apiDiscordLevelsMedalsGet(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/levels/medals/get
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	Search:StorageTransformer = StorageTransformer()
	Search["guild_id"] = Data.getStr("guild_id", UNDEFINED, must_be_digit=True)
	Search["medal_id"] = Data.getStr("medal_id", UNDEFINED, must_be_digit=True)
	Search["member_id"] = Data.getStr("member_id", UNDEFINED, must_be_digit=True)
	Search["name"] = Data.getStr("name", UNDEFINED, len_max=512)
	Search["name_contains"] = Data.getStr("name_contains", UNDEFINED, len_max=512)
	Search["limit"] = Data.getInt("limit", DEFAULT_LIMIT, min_x=1, max_x=MAX_LIMIT)
	Search["offset"] = Data.getInt("offset", 0, min_x=0)

	if not Search["guild_id"]:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(Search["guild_id"]))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	# get medals
	res_medals:list = await getDiscordUsersMedals(PhaazeDiscord, **Search.getAllTransform())

	result:Dict[str, Any] = dict(
		result=[Medal.toJSON() for Medal in res_medals],
		limit=Search["limit"],
		offset=Search["offset"],
		total=await getDiscordUsersMedals(PhaazeDiscord, count_mode=True, **Search.getAllTransform()),
		status=200
	)

	return cls.response(
		text=json.dumps(result),
		content_type="application/json",
		status=200
	)
