from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.index import WebIndex

import discord
import html
from aiohttp.web import Response, Request
from Utils.Classes.htmlformatter import HTMLFormatter
from Utils.Classes.discordwebuserinfo import DiscordWebUserInfo
from Platforms.Web.utils import getNavbar
from .discordinvite import discordInvite
from ..errors import notAllowed

async def discordDashboard(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /discord/dashboard/{guild_id:\d+}
	"""
	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	if not PhaazeDiscord: return await notAllowed(cls, WebRequest, msg="Discord module is not active")

	guild_id:str = WebRequest.match_info.get("guild_id", "")
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id if guild_id.isdigit() else 0))

	if not Guild:
		return await discordInvite(cls, WebRequest, msg=f"Phaaze is not on this Server", guild_id=guild_id)

	DiscordUser:DiscordWebUserInfo = await cls.getDiscordUserInfo(WebRequest)
	if not DiscordUser.found: return await cls.discordLogin(WebRequest)

	DiscordDash:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Discord/Dashboard/main.html")
	DiscordDash.replace(
		location_home = HTMLFormatter("Platforms/Web/Content/Html/Discord/Dashboard/location_home.html"),
		location_configs = HTMLFormatter("Platforms/Web/Content/Html/Discord/Dashboard/location_configs.html"),
		location_commands = HTMLFormatter("Platforms/Web/Content/Html/Discord/Dashboard/location_commands.html"),
		location_levels = HTMLFormatter("Platforms/Web/Content/Html/Discord/Dashboard/location_levels.html"),
		location_quotes = HTMLFormatter("Platforms/Web/Content/Html/Discord/Dashboard/location_quotes.html"),
		location_twitch_alerts = HTMLFormatter("Platforms/Web/Content/Html/Discord/Dashboard/location_twitch_alerts.html"),
		location_assign_roles = HTMLFormatter("Platforms/Web/Content/Html/Discord/Dashboard/location_assign_roles.html")
	)
	# make it twice, since some included locations also have replaceable items
	DiscordDash.replace(
		guild_name = html.escape(Guild.name),
		guild_id = Guild.id,
		web_root = cls.Web.BASE.Vars.WEB_ROOT
	)

	site:str = cls.HTMLRoot.replace(
		replace_empty = True,

		title = f"Phaaze | Discord - Dashboard: {Guild.name}",
		header = getNavbar(active="discord"),
		main = DiscordDash
	)

	return cls.response(
		body=site,
		status=200,
		content_type='text/html'
	)
