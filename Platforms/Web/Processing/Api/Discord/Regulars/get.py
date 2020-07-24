from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.discordregular import DiscordRegular
from Platforms.Discord.db import getDiscordServerRegulars, getDiscordServerRegularAmount
from Platforms.Web.Processing.Api.errors import apiMissingData
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown

DEFAULT_LIMIT:int = 50
MAX_LIMIT:int = 100

async def apiDiscordRegularsGet(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
	Default url: /api/discord/regulars/get
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	regular_id:str = Data.getStr("regular_id", "", must_be_digit=True)
	member_id:str = Data.getStr("member_id", "", must_be_digit=True)
	nickname:bool = Data.getBool("nickname", False) # usernames or nicknames?
	detailed:bool = Data.getBool("detailed", False) # with names, avatar hash etc.
	limit:int = Data.getInt("limit", DEFAULT_LIMIT, min_x=1, max_x=MAX_LIMIT)
	offset:int = Data.getInt("offset", 0, min_x=0)

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	# get regulars
	res_regulars:List[DiscordRegular] = await getDiscordServerRegulars(PhaazeDiscord, guild_id=guild_id, regular_id=regular_id, member_id=member_id, limit=limit, offset=offset)

	return_list:List[dict] = []

	for Regular in res_regulars:

		reg:dict = Regular.toJSON()

		if detailed:
			Mem:discord.Member = Guild.get_member(int(Regular.member_id))
			reg["avatar"] = Mem.avatar if Mem else None

			if not Mem:
				reg["username"] = "[N/A]"
			else:
				if nickname and Mem.nick:
					reg["username"] = Mem.nick
				else:
					reg["username"] = Mem.name

		return_list.append(reg)

	return cls.response(
		text=json.dumps( dict(
			result=return_list,
			detailed=detailed,
			total=(await getDiscordServerRegularAmount(PhaazeDiscord, guild_id)),
			limit=limit,
			offset=offset,
			status=200)
		),
		content_type="application/json",
		status=200
	)
