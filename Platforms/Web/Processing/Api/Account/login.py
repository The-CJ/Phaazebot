from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
import traceback
from aiohttp.web import Response, Request
from Utils.Classes.webuserinfo import WebUserInfo
from Platforms.Discord.api import translateDiscordToken, getDiscordUser
from Utils.stringutils import randomString
from Platforms.Web.Processing.Api.errors import apiNotAllowed, apiUserNotFound, apiMissingData

SESSION_EXPIRE:int = 60*60*24*7 # 1 week

async def apiAccountLoginPhaaze(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/phaaze/login
		looks like all other WebUser pairs, except this time it should be a post request, leading new information to login,
		create session and give this to the user
	"""
	WebUser:WebUserInfo = await cls.getWebUserInfo(WebRequest, force_method="getFromPost")

	if not WebUser.tried:
		return await apiMissingData(cls, WebRequest)

	if not WebUser.found:
		return await apiUserNotFound(cls, WebRequest)

	session_key:str = randomString(size=32)

	cls.Web.BASE.PhaazeDB.insertQuery(
		table = "session_phaaze",
		content = dict(
			session = session_key,
			user_id = WebUser.user_id
		)
	)

	cls.Web.BASE.PhaazeDB.query("""
		UPDATE `user`
		SET `last_login` = NOW()
		WHERE `user`.`id` = %s""",
		(WebUser.user_id,)
	)

	cls.Web.BASE.Logger.debug(f"(API) New Login - Session: {session_key} User: {str(WebUser.username)}", require="api:login")
	return cls.response(
		text=json.dumps( dict(phaaze_session=session_key, status=200, expires_in=str(SESSION_EXPIRE)) ),
		content_type="application/json",
		status=200
	)

async def apiAccountLoginDiscord(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/discord/login
		This sould only be called by Discord after a user successfull authorise
	"""
	data:dict or None = await translateDiscordToken(cls.Web.BASE, WebRequest)
	error:str = ""

	if not data:
		error = "missing"
		cls.Web.BASE.Logger.debug(f"(API/Discord) Failed login, never got called", require="discord:api")
	elif data.get("error", None):
		error = "discord"
		cls.Web.BASE.Logger.debug(f"(API/Discord) Failed login: {str(data)}", require="discord:api")
	else:
		return await completeDiscordTokenLogin(cls, WebRequest, data)

	return cls.response(
		status=302,
		headers = { "Location": f"/discord/login?error={error}" }
	)

async def apiAccountLoginTwitch(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/twitch/login
		This sould only be called by twitch after a user successfull authorised
	"""
	return await apiNotAllowed(cls, WebRequest, msg="Under construction")

# # #

async def completeDiscordTokenLogin(cls:"WebIndex", WebRequest:Request, data:dict) -> Response:

	session_key:str = randomString(size=32)
	access_token:str = data.get('access_token', "")
	refresh_token:str = data.get('refresh_token', "")
	scope:str = data.get('scope', "")
	token_type:str = data.get('token_type', None)
	user_info:dict = await getDiscordUser(cls.Web.BASE, access_token)

	try:
		cls.Web.BASE.PhaazeDB.insertQuery(
			table = "session_discord",
			content = dict(
				session = session_key,
				access_token = access_token,
				refresh_token = refresh_token,
				scope = scope,
				token_type = token_type,
				user_info = json.dumps(user_info)
			)
		)

		cls.Web.BASE.Logger.debug(f"(API) New Discord Login - Session: {session_key} User: {str(user_info.get('username','[N/A]'))}", require="api:login")
		return cls.response(
			status=302,
			headers = {
				"Set-Cookie": f"phaaze_discord_session={session_key}; Path=/; Max-Age={SESSION_EXPIRE};",
				"Location": "/discord"
			}
		)
	except Exception as e:
		tb:str = traceback.format_exc()
		cls.Web.BASE.Logger.error(f"(API) Database error: {str(e)}\n{tb}")
		return cls.response(
			status=302,
			headers = {"Location": "/discord/login?error=database"}
		)
