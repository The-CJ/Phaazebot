from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.undefined import UNDEFINED
from Platforms.Discord.utils import getDiscordServerAssignRoles
from Platforms.Web.Processing.Api.errors import apiMissingData
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown

DEFAULT_LIMIT:int = 50
MAX_LIMIT:int = 100

async def apiDiscordAssignrolesGet(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/assignroles/get
	"""
	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	# get required stuff
	guild_id:str = Data.getStr("guild_id", "", must_be_digit=True)
	role_id:int = Data.getInt("role_id", UNDEFINED, min_x=1)
	assignrole_id:int = Data.getInt("assignrole_id", UNDEFINED, min_x=1)
	limit:int = Data.getInt("limit", DEFAULT_LIMIT, min_x=1, max_x=MAX_LIMIT)
	offset:int = Data.getInt("offset", 0, min_x=0)

	# checks
	if not guild_id:
		return await apiMissingData(cls, WebRequest, msg="missing or invalid 'guild_id'")

	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))
	if not Guild:
		return await apiDiscordGuildUnknown(cls, WebRequest)

	assignroles:list = await getDiscordServerAssignRoles(PhaazeDiscord, guild_id=guild_id, role_id=role_id, assignrole_id=assignrole_id, limit=limit, offset=offset)

	return cls.response(
		text=json.dumps( dict(
			result=[ ARole.toJSON() for ARole in assignroles ],
			status=200)
		),
		content_type="application/json",
		status=200
	)
