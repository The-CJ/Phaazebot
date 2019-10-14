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
from Utils.Classes.discordleveluser import DiscordLevelUser
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown

DEFAULT_LIMIT:int = 50
MAX_LIMIT:int = 100

async def apiDiscordLevelsGet(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/levels/get
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	guild_id:str = Data.get("guild_id")
	if not guild_id:
		return await missingData(cls, WebRequest, msg="missing 'guild_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	# limit
	limit:str = str(Data.get("limit", DEFAULT_LIMIT))
	if limit and not limit.isdigit():
		return await missingData(cls, WebRequest, msg="invalid 'limit'")
		if int(limit) > MAX_LIMIT:
			return await missingData(cls, WebRequest, msg=f"'limit' to high, max = {MAX_LIMIT}")
	limit:int = int(limit or DEFAULT_LIMIT)

	# offset
	offset:str = str(Data.get("offset", 0))
	if offset and not offset.isdigit():
		return await missingData(cls, WebRequest, msg="invalid 'offset'")
	offset:int = int(offset)

	# one member
	member_id:str = Data.get("member_id")
	if member_id and not member_id.isdigit():
		return await missingData(cls, WebRequest, msg="invalid 'member_id'")

	levels:list = await getDiscordServerLevels(PhaazeDiscord, guild_id=guild_id, member_id=member_id, limit=limit, offset=offset)

	if not levels:
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

		return_list.append(level_user)

	return cls.response(
		text=json.dumps( dict(result=return_list, limit=limit, offset=offset, status=200) ),
		content_type="application/json",
		status=200
	)
