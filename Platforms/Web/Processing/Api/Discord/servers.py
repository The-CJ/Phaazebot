from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request
# from Utils.Classes.webuserinfo import WebUserInfo
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

	print(servers)

	return cls.response(
		body=json.dumps(dict(result=servers, status=200)),
		status=200,
		content_type='application/json'
	)
