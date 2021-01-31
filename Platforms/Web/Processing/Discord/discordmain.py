from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb
	from Platforms.Discord.main_discord import PhaazebotDiscord

from aiohttp.web import Response
from Utils.Classes.authdiscordwebuser import AuthDiscordWebUser
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.htmlformatter import HTMLFormatter
from Platforms.Web.index import PhaazeWebIndex
from Platforms.Web.utils import getNavbar, authDiscordWebUser

@PhaazeWebIndex.get("/discord")
async def discordMain(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /discord
	"""
	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	if not PhaazeDiscord: return await cls.Tree.errors.notAllowed(cls, WebRequest, msg="Discord module is not active")

	AuthDiscord:AuthDiscordWebUser = await authDiscordWebUser(cls, WebRequest)
	if not AuthDiscord.found: return await cls.Tree.Discord.discordlogin.discordLogin(cls, WebRequest)

	DiscordMain:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Discord/main.html")

	site:str = cls.HTMLRoot.replace(
		replace_empty=True,

		title="Phaaze | Discord",
		header=getNavbar(active="discord"),
		main=DiscordMain
	)

	return cls.response(
		body=site,
		status=200,
		content_type='text/html'
	)
