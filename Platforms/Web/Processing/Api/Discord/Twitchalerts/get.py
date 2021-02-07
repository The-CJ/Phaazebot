from typing import TYPE_CHECKING, List, Dict, Any
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.main_web import PhaazebotWeb

import json
import discord
from aiohttp.web import Response
from Utils.Classes.storagetransformer import StorageTransformer
from Utils.Classes.discordtwitchalert import DiscordTwitchAlert
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.undefined import UNDEFINED
from Platforms.Discord.db import getDiscordServerTwitchAlerts
from Platforms.Web.Processing.Api.errors import apiMissingData
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown

DEFAULT_LIMIT:int = 50
MAX_LIMIT:int = 100

async def apiDiscordTwitchalertsGet(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/twitchalerts/get
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	Search:StorageTransformer = StorageTransformer()
	Search["discord_guild_id"] = Data.getStr("guild_id", UNDEFINED, must_be_digit=True)
	Search["alert_id"] = Data.getInt("alert_id", UNDEFINED, min_x=1)
	Search["limit"] = Data.getInt("limit", DEFAULT_LIMIT, min_x=1, max_x=MAX_LIMIT)
	Search["offset"] = Data.getInt("offset", 0, min_x=0)

	# checks
	if not Search["discord_guild_id"]:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(Search["discord_guild_id"]))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	# get alerts
	res_alerts:List[DiscordTwitchAlert] = await getDiscordServerTwitchAlerts(PhaazeDiscord, **Search.getAllTransform())

	# if only one is requested, also send custom content
	with_message:bool = True if Search["alert_id"] else False

	result:Dict[str, Any] = dict(
		result=[Alert.toJSON(custom_msg=with_message) for Alert in res_alerts],
		limit=Search["limit"],
		offset=Search["offset"],
		total=await getDiscordServerTwitchAlerts(PhaazeDiscord, count_mode=True, **Search.getAllTransform()),
		status=200
	)

	return cls.response(
		text=json.dumps(result),
		content_type="application/json",
		status=200
	)
