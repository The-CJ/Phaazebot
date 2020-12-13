from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request
from Utils.Classes.webuserinfo import WebUserInfo
from Utils.Classes.discordwebuserinfo import DiscordWebUserInfo
from Utils.Classes.twitchwebuserinfo import TwitchWebUserInfo
from Platforms.Web.Processing.Api.errors import apiUserNotFound

async def apiAccountLogoutPhaaze(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
	Default url: /api/account/phaaze/logout
	"""
	WebUser:WebUserInfo = await cls.getWebUserInfo(WebRequest)

	if not WebUser.found:
		return await apiUserNotFound(cls, WebRequest, msg="Not logged in")

	cls.Web.BASE.PhaazeDB.deleteQuery("""
		DELETE FROM `session_phaaze`
		WHERE `session_phaaze`.`user_id` = %s""",
		(WebUser.user_id,)
	)

	cls.Web.BASE.Logger.debug(f"(API) Logout - User: {WebUser.username}", require="api:logout")
	return cls.response(
		text=json.dumps( dict(status=200) ),
		content_type="application/json",
		status=200
	)

async def apiAccountLogoutDiscord(cls:"WebIndex", WebRequest:Request) -> Response:
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

async def apiAccountLogoutTwitch(cls:"WebIndex", WebRequest:Request) -> Response:
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
