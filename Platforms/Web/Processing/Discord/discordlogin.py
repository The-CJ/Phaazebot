from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb
	from Platforms.Discord.main_discord import PhaazebotDiscord

from aiohttp.web import Response
from Utils.Classes.authdiscordwebuser import AuthDiscordWebUser
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.htmlformatter import HTMLFormatter
from Platforms.Web.utils import getNavbar, authDiscordWebUser
from Platforms.Discord.api import generateDiscordAuthLink
from Platforms.Web.index import PhaazeWebIndex

@PhaazeWebIndex.get("/discord/login")
async def discordLogin(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, msg:str="") -> Response:
	"""
	Default url: /discord/login
	"""
	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	if not PhaazeDiscord: return await cls.Tree.errors.notAllowed(cls, WebRequest, msg="Discord module is not active")

	AuthDiscord:AuthDiscordWebUser = await authDiscordWebUser(cls, WebRequest)
	if AuthDiscord.found: return await cls.Tree.Discord.discordmain.discordMain(cls, WebRequest)

	query_error:str = WebRequest.query.get("error", '')
	if query_error == "missing": msg = "Missing code from Discord"
	elif query_error == "discord": msg = "Error while getting information's from Discord"
	elif query_error == "database": msg = "Error while inserting data into database"

	DiscordLogin:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Discord/login.html")
	DiscordLogin.replace(
		replace_empty=True,

		msg=msg,
		login_link=generateDiscordAuthLink(cls.BASE)
	)

	site:str = cls.HTMLRoot.replace(
		replace_empty=True,

		title="Phaaze | Discord - Login",
		header=getNavbar(active="discord"),
		main=DiscordLogin
	)

	return cls.response(
		body=site,
		status=200,
		content_type='text/html'
	)
