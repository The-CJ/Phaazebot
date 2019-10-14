from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Web.Processing.Api.errors import missingData
from Platforms.Discord.utils import getDiscordServerLevels
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown

DEFAULT_LIMIT:int = 50
MAX_LIMIT:int = 100

async def apiDiscordLevelsGet(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/levels/get
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	if not guild_id:
		return await missingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	# limit
	limit:int = Data.getInt("limit", DEFAULT_LIMIT, min_x=1, max_x=MAX_LIMIT)
	if limit == None:
		return await missingData(cls, WebRequest, msg=f"invalid 'limit', min=1, max={MAX_LIMIT}")

	# offset
	offset:int = Data.getInt("offset", 0, min_x=0)

	# one member
	member_id:str = Data.getStr("member_id", "", must_be_digit=True)

	# with names
	named:bool = Data.getBool("named", False)

	# order by
	order:str = Data.getStr("order", "", transform="lower")
	if order == "exp":
		order = "ORDER BY `exp`"
	elif order == "id":
		order = "ORDER BY `id`"
	elif order == "member_id":
		order = "ORDER BY `member_id`"
	else:
		order = "ORDER BY `rank`"

	levels:list = await getDiscordServerLevels(PhaazeDiscord, guild_id=guild_id, member_id=member_id, limit=limit, offset=offset, order_str=order)

	# stop it
	if not levels:
		if member_id:
			return await apiDiscordGuildUnknown(cls, WebRequest, msg="Could not find a level for this user")
		else:
			return await apiDiscordGuildUnknown(cls, WebRequest, msg="Could not find levels for this guild")

	return_list:list = list()

	for LevelUser in levels:
		level_user:dict = dict(
			member_id = LevelUser.member_id,
			rank = LevelUser.rank,
			exp = LevelUser.exp,
			edited = True if LevelUser.edited else False,
			medals = LevelUser.medals
		)

		if named:
			Mem:discord.Member = Guild.get_member(int(LevelUser.member_id))
			level_user["username"] = Mem.name if Mem else "[N/A]"

		return_list.append(level_user)

	return cls.response(
		text=json.dumps( dict(result=return_list, limit=limit, offset=offset, named=named, status=200) ),
		content_type="application/json",
		status=200
	)
