from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from Platforms.Discord.main_discord import PhaazebotDiscord

import json
import discord
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
# from Utils.Classes.discorduserinfo import DiscordUserInfo
from ..errors import apiNotAllowed, missingData, apiWrongData # apiMissingAuthorisation

async def apiDiscordGuild(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/guild
	"""
	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	if not PhaazeDiscord: return await apiNotAllowed(cls, WebRequest, msg="Discord module is not active")

	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	guild_id:str = Data.get("guild_id")
	if not guild_id:
		return await missingData(cls, WebRequest, msg="missing 'guild_id'")

	if not guild_id.isdigit():
		return await apiWrongData(cls, WebRequest, msg="'guild_id' must be number")


	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))

	if not Guild:
		return cls.response(
			body=json.dumps(dict(msg="could not find a phaaze known guild", status=400)),
			status=400,
			content_type='application/json'
		)

	result:dict = dict(
		name = [],
		avatar = []
	)

	return cls.response(
		body=json.dumps(dict(result=result, status=200)),
		status=200,
		content_type='application/json'
	)
