from typing import TYPE_CHECKING, Dict, Any
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.main_web import PhaazebotWeb

import json
import discord
from aiohttp.web import Response
from Utils.Classes.storagetransformer import StorageTransformer
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.undefined import UNDEFINED
from Platforms.Discord.db import getDiscordServerUsers
from Platforms.Discord.levels import Calc as LevelCalc
from Platforms.Web.Processing.Api.errors import apiMissingData
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown

DEFAULT_LIMIT:int = 50
MAX_LIMIT:int = 100

async def apiDiscordLevelsGet(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/levels/get
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	Search:StorageTransformer = StorageTransformer()

	Search["guild_id"] = Data.getStr("guild_id", UNDEFINED, must_be_digit=True)
	Search["member_id"] = Data.getStr("member_id", UNDEFINED, must_be_digit=True)
	Search["detailed"] = Data.getBool("detailed", False) # with names, avatar hash etc.
	Search["nickname"] = Data.getBool("nickname", False) # usernames or nicknames?
	Search["name_contains"] = Data.getStr("name_contains", UNDEFINED)
	Search["edited"] = Data.getInt("edited", UNDEFINED) # 0 = only non-edited, 1 = only edited
	Search["order"] = Data.getStr("order", UNDEFINED)
	Search["limit"] = Data.getInt("limit", DEFAULT_LIMIT, min_x=1, max_x=MAX_LIMIT)
	Search["offset"] = Data.getInt("offset", 0, min_x=0)

	# checks
	if not Search["guild_id"]:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	# format
	if Search["order"] == "id":
		Search["order_str"] = "ORDER BY `id`"
	elif Search["order"] == "member_id":
		Search["order_str"] = "ORDER BY `member_id`"
	elif Search["order"] == "currency":
		Search["order_str"] = "ORDER BY `currency` DESC"
	else:
		Search["order_str"] = "ORDER BY `exp` DESC"

	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(Search["guild_id"]))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	# get levels
	res_levels:list = await getDiscordServerUsers(PhaazeDiscord, **Search.getAllTransform())

	return_list:list = list()

	for LevelUser in res_levels:

		level_user:dict = LevelUser.toJSON()

		if Search["detailed"]:
			Mem:discord.Member = Guild.get_member(int(LevelUser.member_id))
			level_user["avatar"] = Mem.avatar if Mem else None
			level_user["level"] = LevelCalc.getLevel(LevelUser.exp)
			if not Mem:
				level_user["username"] = "[N/A]"
			else:
				if Search["nickname"] and Mem.nick:
					level_user["username"] = Mem.nick
				else:
					level_user["username"] = Mem.name

		return_list.append(level_user)

	result:Dict[str, Any] = dict(
		result=return_list,
		total=await getDiscordServerUsers(PhaazeDiscord, count_mode=True, **Search.getAllTransform()),
		limit=Search["limit"],
		offset=Search["offset"],
		detailed=Search["detailed"],
		status=200
	)

	return cls.response(
		text=json.dumps(result),
		content_type="application/json",
		status=200
	)
