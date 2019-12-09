from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Platforms.Web.Processing.Api.errors import missingData
from Platforms.Discord.utils import getDiscordServerAssignRoles, getDiscordServerAssignRoleAmount
from Platforms.Web.Processing.Api.Discord.errors import apiDiscordGuildUnknown
from Utils.Classes.undefined import UNDEFINED

DEFAULT_LIMIT:int = 50
MAX_LIMIT:int = 100

async def apiDiscordAssignrolesGet(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/assignroles/get
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

	# only one
	role_id:int = Data.getInt("role_id", UNDEFINED, min_x=1)

	assignroles:list = await getDiscordServerAssignRoles(PhaazeDiscord, guild_id=guild_id, role_id=role_id)

	return_list:list = list()

	for ARole in assignroles:
		return_list.append(ARole.toJSON())

	return cls.response(
		text=json.dumps( dict(
			result=return_list,
			total=(await getDiscordServerAssignRoleAmount(PhaazeDiscord, guild_id=guild_id)),
			status=200)
		),
		content_type="application/json",
		status=200
	)
