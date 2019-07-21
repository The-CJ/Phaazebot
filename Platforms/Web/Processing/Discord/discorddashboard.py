from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.index import WebIndex

import discord
from aiohttp.web import Response, Request
from Utils.Classes.htmlformatter import HTMLFormatter
from Utils.Classes.discorduserinfo import DiscordUserInfo
from Platforms.Web.utils import getNavbar
from ..errors import notAllowed

async def discordDashboard(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /discord/dashboard/{guild_id:\d+}
	"""
	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	if not PhaazeDiscord: return await notAllowed(cls, WebRequest, msg="Discord module is not active")

	guild_id:str = WebRequest.match_info.get("guild_id", "")
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id if guild_id.isdigit() else 0))

	print(Guild)

	DiscordUser:DiscordUserInfo = await cls.getDiscordUserInfo(WebRequest)
	if not DiscordUser.found: return await cls.discordLogin(WebRequest)

	DiscordDash:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Discord/dashboard.html")
	DiscordDash.replace(
		guild_name = Guild.name
	)

	site:str = cls.HTMLRoot.replace(
		replace_empty = True,

		title = "Phaaze | Discord - Dashboard",
		header = getNavbar(active="discord"),
		main = DiscordDash
	)

	return cls.response(
		body=site,
		status=200,
		content_type='text/html'
	)
