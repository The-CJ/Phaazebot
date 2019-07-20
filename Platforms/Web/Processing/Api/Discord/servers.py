from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
import discord
from aiohttp.web import Response, Request
from Platforms.Discord.api import getDiscordUserServers
from Utils.Classes.discorduserinfo import DiscordUserInfo
from ..errors import apiMissingAuthorisation

async def apiDiscordGuilds(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/guilds
	"""

	DiscordUser:DiscordUserInfo = await cls.getDiscordUserInfo(WebRequest)

	if not DiscordUser.found:
		return await apiMissingAuthorisation(cls, WebRequest)

	guilds:dict = await getDiscordUserServers(cls.Web.BASE, DiscordUser.access_token)

	for guild in guilds:
		Perm:discord.Permissions = discord.Permissions(permissions=guild.get("permissions", 0))
		if Perm.administrator or Perm.manage_guild:
			guild["manage"] = True
		else:
			guild["manage"] = False

	return cls.response(
		body=json.dumps(dict(result=guilds, status=200)),
		status=200,
		content_type='application/json'
	)
