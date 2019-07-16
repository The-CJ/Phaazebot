from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

from aiohttp.web import Response, Request
from Utils.Classes.htmlformatter import HTMLFormatter
from Utils.Classes.discorduserinfo import DiscordUserInfo
from Platforms.Web.utils import getNavbar
from Platforms.Discord.api import translateDiscordToken

async def discordLogin(cls:"WebIndex", WebRequest:Request, msg:str="") -> Response:
	"""
		Default url: /discord/login
	"""
	DiscordUser:DiscordUserInfo = await cls.getDiscordUserInfo(WebRequest)
	if DiscordUser.found: return await cls.discordMain(WebRequest)

	# use has a ?code=something -> check login
	if WebRequest.query.get("code", False):
		data:dict or None = await translateDiscordToken(cls.Web.BASE, WebRequest)
		if not data: msg = "Login failed..."
		elif data.get("error", None): msg = "Login failed...."
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
	pass