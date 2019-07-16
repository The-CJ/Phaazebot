from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

from aiohttp.web import Response, Request
from Utils.Classes.htmlformatter import HTMLFormatter
from Utils.Classes.discorduserinfo import DiscordUserInfo
from Platforms.Web.utils import getNavbar

async def discordLogin(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /discord/login
	"""
	DiscordUser:DiscordUserInfo = await cls.getDiscordUserInfo(WebRequest)
	if DiscordUser.found: return await cls.discordMain(WebRequest)

	DiscordLogin:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Discord/login.html")

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
