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
from Utils.Classes.discordregular import DiscordRegular
from Utils.Classes.undefined import UNDEFINED
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown
from Platforms.Web.Processing.Api.errors import apiMissingData
from Platforms.Discord.db import getDiscordServerRegulars

DEFAULT_LIMIT:int = 50
MAX_LIMIT:int = 100

async def apiDiscordRegularsGet(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/regulars/get
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	Search:StorageTransformer = StorageTransformer()
	Search["guild_id"] = Data.getStr("guild_id", UNDEFINED, must_be_digit=True)
	Search["regular_id"] = Data.getStr("regular_id", UNDEFINED, must_be_digit=True)
	Search["member_id"] = Data.getStr("member_id", UNDEFINED, must_be_digit=True)
	Search["nickname"] = Data.getBool("nickname", False) # usernames or nicknames?
	Search["detailed"] = Data.getBool("detailed", False) # with names, avatar hash etc.
	Search["limit"] = Data.getInt("limit", DEFAULT_LIMIT, min_x=1, max_x=MAX_LIMIT)
	Search["offset"] = Data.getInt("offset", 0, min_x=0)

	# checks
	if not Search["guild_id"]:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(Search["guild_id"]))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	# get regulars
	res_regulars:List[DiscordRegular] = await getDiscordServerRegulars(PhaazeDiscord, **Search.getAllTransform())

	return_list:List[dict] = []

	for Regular in res_regulars:

		reg:dict = Regular.toJSON()

		if Search["detailed"]:
			Mem:discord.Member = Guild.get_member(int(Regular.member_id))
			reg["avatar"] = Mem.avatar if Mem else None

			if not Mem:
				reg["username"] = "[N/A]"
			else:
				if Search["nickname"] and Mem.nick:
					reg["username"] = Mem.nick
				else:
					reg["username"] = Mem.name

		return_list.append(reg)

	result:Dict[str, Any] = dict(
		result=return_list,
		detailed=Search["detailed"],
		total=await getDiscordServerRegulars(PhaazeDiscord, count_mode=True, **Search.getAllTransform()),
		limit=Search["limit"],
		offset=Search["offset"],
		status=200
	)

	return cls.response(
		text=json.dumps(result),
		content_type="application/json",
		status=200
	)
