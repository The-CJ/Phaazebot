from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Discord.utils import getDiscordServerUsers, getDiscordServerUserAmount
from Platforms.Discord.levels import Calc as LevelCalc
from Platforms.Web.Processing.Api.errors import apiMissingData
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown

DEFAULT_LIMIT:int = 50
MAX_LIMIT:int = 100

async def apiDiscordLevelsGet(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/levels/get
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	limit:int = Data.getInt("limit", DEFAULT_LIMIT, min_x=1, max_x=MAX_LIMIT)
	offset:int = Data.getInt("offset", 0, min_x=0)
	member_id:str = Data.getStr("member_id", "", must_be_digit=True)
	detailed:bool = Data.getBool("detailed", False) # with names, avatar hash etc.
	nickname:bool = Data.getBool("nickname", False) # usernames or nicknames?
	name_contains:str = Data.getStr("name_contains", "")
	order:str = Data.getStr("order", "").lower() # order by
	edited:int = Data.getInt("edited", 0, min_x=0, max_x=2) # 0 = all, 1 = only nonedited, 2 = only edited

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	# format
	if order == "id":
		order = "ORDER BY `id`"
	elif order == "member_id":
		order = "ORDER BY `member_id`"
	elif order == "currency":
		order = "ORDER BY `currency`"
	else:
		order = "ORDER BY `rank`, `exp`"

	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	# get levels
	res_levels:list = await getDiscordServerUsers(PhaazeDiscord, guild_id=guild_id, member_id=member_id, limit=limit, offset=offset, order_str=order, edited=edited, name_contains=name_contains)

	return_list:list = list()

	for LevelUser in res_levels:

		level_user:dict = LevelUser.toJSON()

		if detailed:
			Mem:discord.Member = Guild.get_member(int(LevelUser.member_id))
			level_user["avatar"] = Mem.avatar if Mem else None
			level_user["level"] = LevelCalc.getLevel(LevelUser.exp)
			if not Mem:
				level_user["username"] = "[N/A]"
			else:
				if nickname and Mem.nick:
					level_user["username"] = Mem.nick
				else:
					level_user["username"] = Mem.name

		return_list.append(level_user)

	return cls.response(
		text=json.dumps( dict(
			result=return_list,
			total=await getDiscordServerUserAmount(PhaazeDiscord, guild_id),
			limit=limit,
			offset=offset,
			detailed=detailed,
			status=200)
		),
		content_type="application/json",
		status=200
	)
