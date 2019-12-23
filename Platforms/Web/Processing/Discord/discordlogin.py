from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.index import WebIndex

from aiohttp.web import Response, Request
from Utils.Classes.htmlformatter import HTMLFormatter
from Utils.Classes.discordwebuserinfo import DiscordWebUserInfo
from Platforms.Web.utils import getNavbar
from ..errors import notAllowed

async def discordLogin(cls:"WebIndex", WebRequest:Request, msg:str="") -> Response:
	"""
		Default url: /discord/login
	"""
	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	if not PhaazeDiscord: return await notAllowed(cls, WebRequest, msg="Discord module is not active")

	DiscordUser:DiscordWebUserInfo = await cls.getDiscordUserInfo(WebRequest)
	if DiscordUser.found: return await cls.discordMain(WebRequest)

	query_error:str = WebRequest.query.get("error", None)
	if query_error == "missing": msg = "Missing code from Discord"
	elif query_error == "discord": msg = "Error while getting informations from Discord"
	elif query_error == "database": msg = "Error while inserting data into database"

	DiscordLogin:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Discord/login.html")
	DiscordLogin.replace(
		replace_empty = True,

		msg = msg,
		login_link = cls.Web.BASE.Vars.DISCORD_LOGIN_LINK
	)

	site:str = cls.HTMLRoot.replace(
		replace_empty = True,

		title = "Phaaze | Discord - Login",
		header = getNavbar(active="discord"),
		main = DiscordLogin
	)

	return cls.response(
		body=site,
		status=200,
		content_type='text/html'
	)
