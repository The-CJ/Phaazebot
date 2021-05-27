from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Twitch.main_twitch import PhaazebotTwitch
	from Platforms.Web.main_web import PhaazebotWeb

from aiohttp.web import Response
from Utils.Classes.authtwitchwebuser import AuthTwitchWebUser
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.htmlformatter import HTMLFormatter
from Platforms.Web.utils import getNavbar, authTwitchWebUser
from Platforms.Twitch.api import generateTwitchAuthLink
from Platforms.Web.index import PhaazeWebIndex

@PhaazeWebIndex.get("/twitch/login")
async def twitchLogin(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, msg:str="") -> Response:
	"""
	Default url: /twitch/login
	"""
	PhaazeTwitch:"PhaazebotTwitch" = cls.BASE.Twitch
	if not PhaazeTwitch:
		return await cls.Tree.errors.notAllowed(cls, WebRequest, msg="Twitch module is not active")

	AuthTwitch:AuthTwitchWebUser = await authTwitchWebUser(cls, WebRequest)
	if AuthTwitch.found:
		return await cls.Tree.Twitch.twitchmain.twitchMain(cls, WebRequest)

	query_error:str = WebRequest.query.get("error", '')
	if query_error == "missing": msg = "Missing code from Twitch"
	elif query_error == "discord": msg = "Error while getting information's from Twitch"
	elif query_error == "database": msg = "Error while inserting data into database"

	TwitchLogin:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Twitch/login.html")
	TwitchLogin.replace(
		replace_empty=True,

		msg=msg,
		login_link=generateTwitchAuthLink(cls.BASE)
	)

	site:str = cls.HTMLRoot.replace(
		replace_empty=True,

		title="Phaaze | Twitch - Login",
		header=getNavbar(active="twitch"),
		main=TwitchLogin
	)

	return cls.response(
		body=site,
		status=200,
		content_type='text/html'
	)
