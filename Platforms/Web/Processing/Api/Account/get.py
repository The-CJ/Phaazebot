from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request
from Utils.Classes.webuserinfo import WebUserInfo
from Utils.Classes.discordwebuserinfo import DiscordWebUserInfo
from Platforms.Web.Processing.Api.errors import apiNotAllowed, apiMissingAuthorisation

async def apiAccountGetPhaaze(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/phaaze/get
	"""
	WebUser:WebUserInfo = await cls.getWebUserInfo(WebRequest)

	if not WebUser.found:
		return await apiMissingAuthorisation(cls, WebRequest)

	return cls.response(
		text=json.dumps( dict(user=WebUser.toJSON(), status=200) ),
		content_type="application/json",
		status=200
	)

async def apiAccountGetDiscord(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/discord/get
	"""
	DiscordUser:DiscordWebUserInfo = await cls.getDiscordUserInfo(WebRequest)

	if not DiscordUser.found:
		return await apiMissingAuthorisation(cls, WebRequest)

	return cls.response(
		text=json.dumps( dict(user=DiscordUser.toJSON(), status=200) ),
		content_type="application/json",
		status=200
	)

async def apiAccountGetTwitch(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/twitch/get
	"""
	return await apiNotAllowed(cls, WebRequest, msg="Under construction")
