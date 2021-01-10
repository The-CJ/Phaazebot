from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

import json
from aiohttp.web import Response
from Utils.Classes.authwebuser import AuthWebUser
from Utils.Classes.discordwebuser import DiscordWebUserInfo
from Utils.Classes.twitchwebuserinfo import TwitchWebUserInfo
from Utils.Classes.extendedrequest import ExtendedRequest
from Platforms.Web.Processing.Api.errors import apiUserNotFound
from Platforms.Web.utils import authWebUser

async def apiAccountLogoutPhaaze(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/account/phaaze/logout
	"""
	AuthWeb:AuthWebUser = await authWebUser(cls, WebRequest)

	if not AuthWeb.found:
		return await apiUserNotFound(cls, WebRequest, msg="Not logged in")

	cls.BASE.PhaazeDB.deleteQuery("""
		DELETE FROM `session_phaaze`
		WHERE `session_phaaze`.`user_id` = %s""",
		(AuthWeb.User.user_id,)
	)

	cls.BASE.Logger.debug(f"(API) Logout - User: {AuthWeb.User.username}", require="api:logout")
	return cls.response(
		text=json.dumps(dict(status=200)),
		content_type="application/json",
		status=200
	)

# TODO: rework
async def apiAccountLogoutDiscord(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/account/discord/logout
	"""

	DiscordUser:DiscordWebUserInfo = await cls.getDiscordUserInfo(WebRequest)

	if not DiscordUser.found:
		return await apiUserNotFound(cls, WebRequest, msg="Not logged in")

	cls.Web.BASE.PhaazeDB.query("""
		DELETE FROM `session_discord`
		WHERE `session_discord`.`access_token` = %s
			OR JSON_EXTRACT(`session_discord`.`user_info`, "$.id") = %s""",
		(DiscordUser.access_token, DiscordUser.user_id)
	)

	cls.Web.BASE.Logger.debug(f"(API/Discord) Discord Logout - User: {DiscordUser.username}", require="api:logout")
	return cls.response(
		text=json.dumps( dict(status=200) ),
		content_type="application/json",
		status=200
	)

# TODO: rework
async def apiAccountLogoutTwitch(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/account/twitch/logout
	"""
	TwitchUser:TwitchWebUserInfo = await cls.getTwitchUserInfo(WebRequest)

	if not TwitchUser.found:
		return await apiUserNotFound(cls, WebRequest, msg="Not logged in")

	cls.Web.BASE.PhaazeDB.query("""
		DELETE FROM `session_twitch`
		WHERE `session_twitch`.`access_token` = %s
			OR JSON_EXTRACT(`session_twitch`.`user_info`, "$.id") = %s""",
		(TwitchUser.access_token, TwitchUser.user_id)
	)

	cls.Web.BASE.Logger.debug(f"(API/Twitch) Discord Logout - User: {TwitchUser.name}", require="api:logout")
	return cls.response(
		text=json.dumps( dict(status=200) ),
		content_type="application/json",
		status=200
	)
