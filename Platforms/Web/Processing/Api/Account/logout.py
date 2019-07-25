from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request
from Utils.Classes.webuserinfo import WebUserInfo
from Utils.Classes.discorduserinfo import DiscordUserInfo
from ..errors import apiNotAllowed, userNotFound

async def apiAccountLogoutPhaaze(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/phaaze/logout
	"""
	UserInfo:WebUserInfo = await cls.getUserInfo(WebRequest)

	if not UserInfo.found:
		return await userNotFound(cls, WebRequest, msg="Not logged in")

	cls.Web.BASE.PhaazeDB.query("""
		DELETE FROM session_phaaze
		WHERE session_phaaze.user_id = %s""",
		(UserInfo.user_id,)
	)

	cls.Web.BASE.Logger.debug(f"(API) Logout - User: {UserInfo.username}", require="api:logout")
	return cls.response(
		text=json.dumps( dict(status=200) ),
		content_type="application/json",
		status=200
	)

async def apiAccountLogoutDiscord(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/discord/logout
	"""

	DiscordUser:DiscordUserInfo = await cls.getDiscordUserInfo(WebRequest)

	if not DiscordUser.found:
		return await userNotFound(cls, WebRequest, msg="Not logged in")

	cls.Web.BASE.PhaazeDB.query("""
		DELETE FROM session_discord
		WHERE session_discord.access_token = %s
			OR JSON_EXTRACT(session_discord.user_info, "$.id") = %s""",
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
	return await apiNotAllowed(cls, WebRequest, msg="Under construction")
