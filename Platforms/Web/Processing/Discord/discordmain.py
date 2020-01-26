from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.index import WebIndex

from aiohttp.web import Response, Request
from Utils.Classes.htmlformatter import HTMLFormatter
from Utils.Classes.discordwebuserinfo import DiscordWebUserInfo
from Platforms.Web.utils import getNavbar
from ..errors import notAllowed

async def discordMain(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /discord
	"""
	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	if not PhaazeDiscord: return await notAllowed(cls, WebRequest, msg="Discord module is not active")

	DiscordUser:DiscordWebUserInfo = await cls.getDiscordUserInfo(WebRequest)
	if not DiscordUser.found: return await cls.discordLogin(WebRequest)

	DiscordMain:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Discord/main.html")

	site:str = cls.HTMLRoot.replace(
		replace_empty = True,

		title = "Phaaze | Discord",
		header = getNavbar(active="discord"),
		main = DiscordMain
	)

	return cls.response(
		body=site,
		status=200,
		content_type='text/html'
	)
