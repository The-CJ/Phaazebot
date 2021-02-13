from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.main_web import PhaazebotWeb

import json
import discord
from aiohttp.web import Response
from Utils.Classes.authdiscordwebuser import AuthDiscordWebUser
from Utils.Classes.extendedrequest import ExtendedRequest
from Platforms.Discord.api import getDiscordUserServers
from Platforms.Web.index import PhaazeWebIndex
from Platforms.Web.utils import authDiscordWebUser

async def apiDiscordUserGuilds(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/userguilds
	"""
	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	if not PhaazeDiscord:
		return await cls.Tree.Api.errors.apiNotAllowed(cls, WebRequest, msg="Discord module is not active")

	AuthDiscord:AuthDiscordWebUser = await authDiscordWebUser(cls, WebRequest)

	if not AuthDiscord.found:
		return await cls.Tree.Api.errors.apiMissingAuthorisation(cls, WebRequest)

	guilds:List[dict] = await getDiscordUserServers(cls.BASE, AuthDiscord.access_token)

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
