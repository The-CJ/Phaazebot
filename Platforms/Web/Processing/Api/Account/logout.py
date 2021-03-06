from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

import json
from aiohttp.web import Response
from Utils.Classes.authdiscordwebuser import AuthDiscordWebUser
from Utils.Classes.authtwitchwebuser import AuthTwitchWebUser
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.authwebuser import AuthWebUser
from Platforms.Web.Processing.Api.errors import apiUserNotFound
from Platforms.Web.utils import authWebUser, authDiscordWebUser, authTwitchWebUser

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

async def apiAccountLogoutDiscord(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/account/discord/logout
	"""

	AuthDiscord:AuthDiscordWebUser = await authDiscordWebUser(cls, WebRequest)

	if not AuthDiscord.found:
		return await apiUserNotFound(cls, WebRequest, msg="Not logged in")

	cls.BASE.PhaazeDB.query("""
		DELETE FROM `session_discord`
		WHERE `session_discord`.`access_token` = %s
			OR JSON_EXTRACT(`session_discord`.`user_info`, "$.id") = %s""",
		(AuthDiscord.access_token, AuthDiscord.User.user_id)
	)

	cls.BASE.Logger.debug(f"(API/Discord) Discord Logout - User: {AuthDiscord.User.username}", require="api:logout")
	return cls.response(
		text=json.dumps(dict(status=200)),
		content_type="application/json",
		status=200
	)

async def apiAccountLogoutTwitch(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/account/twitch/logout
	"""
	AuthTwitch:AuthTwitchWebUser = await authTwitchWebUser(cls, WebRequest)

	if not AuthTwitch.found:
		return await apiUserNotFound(cls, WebRequest, msg="Not logged in")

	cls.BASE.PhaazeDB.query("""
		DELETE FROM `session_twitch`
		WHERE `session_twitch`.`access_token` = %s
			OR JSON_EXTRACT(`session_twitch`.`user_info`, "$.id") = %s""",
		(AuthTwitch.access_token, AuthTwitch.User.user_id)
	)

	cls.BASE.Logger.debug(f"(API/Twitch) Discord Logout - User: {AuthTwitch.User.login}", require="api:logout")
	return cls.response(
		text=json.dumps(dict(status=200)),
		content_type="application/json",
		status=200
	)
