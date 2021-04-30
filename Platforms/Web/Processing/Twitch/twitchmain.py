from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb
	from Platforms.Twitch.main_twitch import PhaazebotTwitch

from aiohttp.web import Response
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.htmlformatter import HTMLFormatter
from Platforms.Web.utils import getNavbar, generateTwitchAuthLink
from Platforms.Web.index import PhaazeWebIndex

@PhaazeWebIndex.get("/twitch")
async def discordMain(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /twitch
	"""
	PhaazeTwitch:"PhaazebotTwitch" = cls.BASE.Twitch
	if not PhaazeTwitch: return await cls.Tree.errors.notAllowed(cls, WebRequest, msg="Twitch module is not active")

	TwitchMain:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Twitch/main.html")
	TwitchMain.replace(
		replace_empty=True,
		twitch_login_link=generateTwitchAuthLink(cls.BASE)
	)

	site:str = cls.HTMLRoot.replace(
		replace_empty=True,

		title="Phaaze | Twitch",
		header=getNavbar(active="twitch"),
		main=TwitchMain
	)

	return cls.response(
		body=site,
		status=200,
		content_type='text/html'
	)
