from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.index import WebIndex

import discord
import html
from aiohttp.web import Response, Request
from Utils.Classes.htmlformatter import HTMLFormatter
from Utils.Classes.discordserversettings import DiscordServerSettings
from Platforms.Discord.db import getDiscordSeverSettings
from Platforms.Web.utils import getNavbar
from ..errors import notAllowed

async def discordLevels(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /discord/levels/{guild_id:\d+}
	"""
	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	if not PhaazeDiscord: return await notAllowed(cls, WebRequest, msg="Discord module is not active")

	guild_id:str = WebRequest.match_info.get("guild_id", "")
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id if guild_id.isdigit() else 0))

	if not Guild:
		return await cls.discordInvite(WebRequest, msg=f"Phaaze is not on this Server", guild_id=guild_id)

	GuildSettings:DiscordServerSettings = await getDiscordSeverSettings(cls.Web.BASE.Discord, guild_id, prevent_new=True)

	currency_name:str = GuildSettings.currency_name if GuildSettings.currency_name else cls.Web.BASE.Vars.default_discord_currency
	currency_name_multi:str = GuildSettings.currency_name_multi if GuildSettings.currency_name_multi else cls.Web.BASE.Vars.default_discord_currency_multi

	DiscordLevels:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Discord/levels.html")
	DiscordLevels.replace(
		guild_name = html.escape(Guild.name),
		guild_id = str(Guild.id),
		guild_currency = currency_name,
		guild_currency_multi = currency_name_multi
	)

	site:str = cls.HTMLRoot.replace(
		replace_empty = True,

		title = f"Phaaze | Discord - levels: {Guild.name}",
		header = getNavbar(active="discord"),
		main = DiscordLevels
	)

	return cls.response(
		body=site,
		status=200,
		content_type='text/html'
	)
