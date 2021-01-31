from typing import TYPE_CHECKING, List, Optional
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

import json
import traceback
from aiohttp.web import Response
from Utils.stringutils import randomString
from Utils.Classes.authwebuser import AuthWebUser
from Utils.Classes.twitchuser import TwitchUser
from Utils.Classes.extendedrequest import ExtendedRequest
from Platforms.Web.utils import authWebUser
from Platforms.Discord.api import translateDiscordToken, getDiscordUser
from Platforms.Twitch.api import translateTwitchToken, getTwitchUsers
from Platforms.Web.Processing.Api.errors import apiUserNotFound, apiMissingData

SESSION_EXPIRE:int = 60*60*24*7 # 1 week

async def apiAccountLoginPhaaze(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/account/phaaze/login
	looks like all other WebUser pairs, except this time it should be a post request, leading new information to login,
	create session and give this to the user
	"""
	AuthWeb:AuthWebUser = await authWebUser(cls, WebRequest, force_method="viaPost")

	if not AuthWeb.tried:
		return await apiMissingData(cls, WebRequest)

	if not AuthWeb.found:
		return await apiUserNotFound(cls, WebRequest)

	session_key:str = randomString(size=32)

	cls.BASE.PhaazeDB.insertQuery(
		table="session_phaaze",
		content=dict(
			session=session_key,
			user_id=AuthWeb.User.user_id
		)
	)

	cls.BASE.PhaazeDB.query("""
		UPDATE `user`
		SET `last_login` = NOW()
		WHERE `user`.`id` = %s""",
		(AuthWeb.User.user_id,)
	)

	cls.BASE.Logger.debug(f"(API) New Login - Session: {session_key} User: {str(AuthWeb.User.username)}", require="api:login")
	return cls.response(
		text=json.dumps(dict(phaaze_session=session_key, status=200, expires_in=str(SESSION_EXPIRE))),
		content_type="application/json",
		status=200
	)

async def apiAccountLoginDiscord(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/account/discord/login
	This should only be called by Discord after a user successful authorise
	"""
	data:Optional[dict] = await translateDiscordToken(cls.BASE, WebRequest)
	error:str

	if not data:
		error = "missing"
		cls.BASE.Logger.debug(f"(API/Discord) Failed login, never got called", require="discord:api")
	elif data.get("error", None):
		error = "discord"
		cls.BASE.Logger.debug(f"(API/Discord) Failed login: {str(data)}", require="discord:api")
	else:
		return await completeDiscordTokenLogin(cls, WebRequest, data)

	return cls.response(
		status=302,
		headers={"Location": f"/discord/login?error={error}"}
	)

# TODO: rework
async def apiAccountLoginTwitch(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/account/twitch/login
	This should only be called by twitch after a user successful authorised
	"""
	data:dict or None = await translateTwitchToken(cls.Web.BASE, WebRequest)
	error:str

	if not data:
		error = "missing"
		cls.Web.BASE.Logger.debug(f"(API/Twitch) Failed login, never got called", require="twitch:api")
	elif data.get("error", None):
		error = "twitch"
		cls.Web.BASE.Logger.debug(f"(API/Twitch) Failed login: {str(data)}", require="twitch:api")
	else:
		return await completeTwitchTokenLogin(cls, WebRequest, data)

	return cls.response(
		status=302,
		headers={"Location": f"/twitch/login?error={error}"}
	)

# # #

async def completeDiscordTokenLogin(cls:"PhaazebotWeb", _WebRequest:ExtendedRequest, data:dict) -> Response:
	"""
	inserts all necessary data into the session_discord database
	"""

	session_key:str = randomString(size=32)
	access_token:str = data.get('access_token', "")
	refresh_token:str = data.get('refresh_token', "")
	scope:str = data.get('scope', "")
	token_type:str = data.get('token_type', "")
	user_info:dict = await getDiscordUser(cls.BASE, access_token)

	# if the result has a message field, something went wrong
	if user_info.get("message", "---") != "---":
		cls.BASE.Logger.warning("(API) Discord user login failed")
		return cls.response(
			status=302,
			headers={"Location": "/discord/login?error=user"}
		)

	try:
		cls.BASE.PhaazeDB.insertQuery(
			table="session_discord",
			content=dict(
				session=session_key,
				access_token=access_token,
				refresh_token=refresh_token,
				scope=scope,
				token_type=token_type,
				user_info=json.dumps(user_info)
			)
		)

		cls.BASE.Logger.debug(f"(API) New Discord Login - Session: {session_key} User: {str(user_info.get('username','[N/A]'))}", require="api:login")
		return cls.response(
			status=302,
			headers={
				"Set-Cookie": f"phaaze_discord_session={session_key}; Path=/; Max-Age={SESSION_EXPIRE};",
				"Location": "/discord"
			}
		)
	except Exception as e:
		tb:str = traceback.format_exc()
		cls.BASE.Logger.error(f"(API) Database error: {str(e)}\n{tb}")
		return cls.response(
			status=302,
			headers={"Location": "/discord/login?error=database"}
		)

# TODO: rework
async def completeTwitchTokenLogin(cls:"PhaazebotWeb", _WebRequest:ExtendedRequest, data:dict) -> Response:
	"""
	inserts all necessary data into the session_twitch database
	"""

	session_key:str = randomString(size=32)
	access_token:str = data.get("access_token", "")
	refresh_token:str = data.get("refresh_token", "")
	scope:str = ' '.join(data.get("scope", []))
	token_type:str = data.get('token_type', "")

	user_res:List[TwitchUser] = await getTwitchUsers(cls.Web.BASE, access_token, item_type="token")
	TwitchAuthUser:TwitchUser = user_res.pop(0) if len(user_res) > 0 else None

	if not TwitchAuthUser or not TwitchAuthUser.extended:
		cls.Web.BASE.Logger.warning("(API) Twitch user login failed")
		return cls.response(
			status=302,
			headers={"Location": "/twitch/login?error=user"}
		)

	try:
		cls.Web.BASE.PhaazeDB.insertQuery(
			table="session_twitch",
			content=dict(
				session=session_key,
				access_token=access_token,
				refresh_token=refresh_token,
				scope=scope,
				token_type=token_type,
				user_info=json.dumps(TwitchAuthUser.toJSON(types=True,images=True,with_email=True))
			)
		)

		cls.Web.BASE.Logger.debug(f"(API) New Twitch Login - Session: {session_key} User: {TwitchAuthUser.name}", require="api:login")
		return cls.response(
			status=302,
			headers={
				"Set-Cookie": f"phaaze_twitch_session={session_key}; Path=/; Max-Age={SESSION_EXPIRE};",
				"Location": "/twitch"
			}
		)
	except Exception as e:
		tb:str = traceback.format_exc()
		cls.Web.BASE.Logger.error(f"(API) Database error: {str(e)}\n{tb}")
		return cls.response(
			status=302,
			headers={"Location": "/twitch/login?error=database"}
		)
