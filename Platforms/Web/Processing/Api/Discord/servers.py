from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
import discord
from aiohttp.web import Response, Request
from Platforms.Discord.api import getDiscordUserServers
from Utils.Classes.discorduserinfo import DiscordUserInfo
from ..errors import apiMissingAuthorisation

async def apiDiscordServers(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/servers
	"""

	DiscordUser:DiscordUserInfo = await cls.getDiscordUserInfo(WebRequest)

	if not DiscordUser.found:
		return await apiMissingAuthorisation(cls, WebRequest)

	servers:dict = await getDiscordUserServers(cls.Web.BASE, DiscordUser.access_token)

	for server in servers:
		Perm:discord.Permissions = discord.Permissions(permissions=server.get("permissions", 0))
		if Perm.administrator or Perm.manage_guild:
			server["manage"] = True
		else:
			server["manage"] = False

	return cls.response(
		body=json.dumps(dict(result=servers, status=200)),
		status=200,
		content_type='application/json'
	)
