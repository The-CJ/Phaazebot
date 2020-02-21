from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.index import WebIndex

import discord
from aiohttp.web import Response, Request
from Utils.Classes.htmlformatter import HTMLFormatter
from Platforms.Web.utils import getNavbar
from ..errors import notAllowed

async def discordView(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /discord/view/{guild_id:\d}
	"""
	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	if not PhaazeDiscord: return await notAllowed(cls, WebRequest, msg="Discord module is not active")

	guild_id:str = WebRequest.match_info.get("guild_id", "")
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))

	if not Guild:
		return await cls.discordInvite(WebRequest, msg=f"Phaaze is not on this Server", guild_id=guild_id)

	ViewPage:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Discord/view.html")
	ViewPage.replace()

	site:str = cls.HTMLRoot.replace(
		replace_empty = True,

		title = "Phaaze | Discord - View",
		header = getNavbar(active="discord"),
		main = ViewPage
	)

	return cls.response(
		body=site,
		status=200,
		content_type='text/html'
	)
