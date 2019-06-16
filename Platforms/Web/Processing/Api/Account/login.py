from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import datetime
import json
from ..errors import apiNotAllowed, userNotFound, missingData
from aiohttp.web import Response, Request
from Utils.Classes.webuserinfo import WebUserInfo
from Utils.stringutils import randomString

async def apiAccountLoginPhaaze(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/phaaze/login
		looks like all other UserInfo pairs, except this time it should be a post request, leading new information to login,
		create session and give this to the user
	"""
	UserInfo:WebUserInfo = await cls.getUserInfo(WebRequest, force_method="getFromPost")

	if not UserInfo.tryed:
		return await missingData(cls, WebRequest)

	if not UserInfo.found:
		return await userNotFound(cls, WebRequest)

	session_key:str = randomString(size=32)
	Expire:datetime.datetime = datetime.datetime.now() + datetime.timedelta(days=30)

	cls.Web.BASE.PhaazeDB.insert(
		into = "session/phaaze",
		content = dict(session=session_key, user_id=UserInfo.user_id, expire=str(Expire) )
	)
	cls.Web.BASE.PhaazeDB.update(
		of = "user",
		where = f"int(data['id']) == int({UserInfo.user_id})",
		content = dict(last_login=str(datetime.datetime.now()))
	)
	cls.Web.BASE.Logger.debug(f"New Login - Session: {session_key} User: {str(UserInfo.username)}", require="api:login")
	return cls.response(
		text=json.dumps( dict(phaaze_session=session_key, status=200, expire=str(Expire)) ),
		content_type="application/json",
		status=200
	)

async def apiAccountLoginDiscord(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/discord/login
		This sould only be called by discord after a user successfull authorised
	"""
	return await apiNotAllowed(cls, WebRequest, msg="Under construction")

async def apiAccountLoginTwitch(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/twitch/login
		This sould only be called by twitch after a user successfull authorised
	"""
	return await apiNotAllowed(cls, WebRequest, msg="Under construction")
