from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

from aiohttp.web import Response, Request
from Utils.Classes.htmlformatter import HTMLFormatter
from Utils.Classes.discorduserinfo import DiscordUserInfo
from Platforms.Web.utils import getNavbar

async def discordMain(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /discord
	"""
	DiscordUser:DiscordUserInfo = await cls.getDiscordUserInfo(WebRequest)
	if not DiscordUser: return None

	DiscordMain:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Discord/main.html")

	site:str = cls.HTMLRoot.replace(
		replace_empty = True,

		title = "Phaaze | Discord",
		header = getNavbar(),
		main = DiscordMain
	)

	return cls.response(
		body=site,
		status=200,
		content_type='text/html'
	)
