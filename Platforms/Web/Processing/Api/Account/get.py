from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

import json
from aiohttp.web import Response
from Utils.Classes.authwebuser import AuthWebUser
from Utils.Classes.discordwebuserinfo import DiscordWebUserInfo
from Utils.Classes.twitchwebuserinfo import TwitchWebUserInfo
from Utils.Classes.extendedrequest import ExtendedRequest
from Platforms.Web.utils import authWebUser, getTwitchUserInfo, getDiscordUserInfo
from Platforms.Web.Processing.Api.errors import apiMissingAuthorisation

async def apiAccountGetPhaaze(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/account/phaaze/get
	"""
	AuthWeb:AuthWebUser = await authWebUser(cls, WebRequest)

	if not AuthWeb.found:
		return await apiMissingAuthorisation(cls, WebRequest)

	return cls.response(
		text=json.dumps(dict(user=AuthWeb.User.toJSON(), status=200)),
		content_type="application/json",
		status=200
	)

# TODO: rework
async def apiAccountGetDiscord(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/account/discord/get
	"""
	DiscordUser:DiscordWebUserInfo = await getDiscordUserInfo(cls, WebRequest)

	if not DiscordUser.found:
		return await apiMissingAuthorisation(cls, WebRequest)

	return cls.response(
		text=json.dumps(dict(user=DiscordUser.toJSON(), status=200)),
		content_type="application/json",
		status=200
	)

# TODO: rework
async def apiAccountGetTwitch(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/account/twitch/get
	"""
	TwitchUser:TwitchWebUserInfo = await getTwitchUserInfo(cls, WebRequest)

	if not TwitchUser.found:
		return await apiMissingAuthorisation(cls, WebRequest)

	return cls.response(
		text=json.dumps(dict(user=TwitchUser.toJSON(), status=200)),
		content_type="application/json",
		status=200
	)
