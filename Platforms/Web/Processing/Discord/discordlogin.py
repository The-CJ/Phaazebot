from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import datetime
from aiohttp.web import Response, Request
from Utils.Classes.htmlformatter import HTMLFormatter
from Utils.Classes.discorduserinfo import DiscordUserInfo
from Platforms.Web.utils import getNavbar
from Platforms.Discord.api import translateDiscordToken, getDiscordUser
from Utils.stringutils import randomString

async def discordLogin(cls:"WebIndex", WebRequest:Request, msg:str="") -> Response:
	"""
		Default url: /discord/login
	"""
	DiscordUser:DiscordUserInfo = await cls.getDiscordUserInfo(WebRequest)
	if DiscordUser.found: return await cls.discordMain(WebRequest)

	# use has a ?code=something -> check login
	if WebRequest.query.get("code", False):
		data:dict or None = await translateDiscordToken(cls.Web.BASE, WebRequest)
		if not data:
			msg = "Login failed..."
			cls.Web.BASE.Logger.debug(f"(Discord) Failed login, never got called", require="discord:api")
		elif data.get("error", None):
			msg = "Login failed...."
			cls.Web.BASE.Logger.debug(f"(Discord) Failed login: {str(data)}", require="discord:api")
		else: return await completeTokenLogin(cls, WebRequest, data)

	DiscordLogin:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Discord/login.html")
	DiscordLogin.replace(
		replace_empty = True,

		msg = msg,
		login_link = cls.Web.BASE.Vars.DISCORD_LOGIN_LINK
	)

	site:str = cls.HTMLRoot.replace(
		replace_empty = True,

		title = "Phaaze | Discord - Login",
		header = getNavbar(),
		main = DiscordLogin
	)

	return cls.response(
		body=site,
		status=200,
		content_type='text/html'
	)

async def completeTokenLogin(cls:"WebIndex", WebRequest:Request, data:dict) -> Response:

	session_key:str = randomString(size=32)
	access_token:str = data.get('access_token', None)
	refresh_token:str = data.get('refresh_token', None)
	scope:str = data.get('scope', None)
	created_at:str = str(datetime.datetime.now())
	user_info:dict = await getDiscordUser(cls.Web.BASE, access_token)

	token_type:str = data.get('token_type', None)

	save:dict = dict(
		session = session_key,
		access_token = access_token,
		refresh_token = refresh_token,
		scope = scope,
		created_at = created_at,
		user_info = user_info
	)

	# only save if it's different, which it shouldn't
	if token_type != "Bearer": save["token_type"] = token_type

	res:dict = cls.Web.BASE.PhaazeDB.insert(
		into = "session/discord",
		content = save
	)

	Expire:datetime.datetime = datetime.datetime.now() + datetime.timedelta(days=7)
	if res.get("status", False) == "inserted":
		return cls.response(
			status=302,
			headers = {
				"Set-Cookie": f"phaaze_discord_session={session_key}; Path=/; expires={Expire.isoformat()};",
				"Location": "/discord"
			}
		)
