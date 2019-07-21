from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.index import WebIndex

import discord
import html
from aiohttp.web import Response, Request
from Utils.Classes.htmlformatter import HTMLFormatter
from Utils.Classes.discordserversettings import DiscordServerSettings
from Platforms.Web.utils import getNavbar
from Platforms.Discord.utils import getDiscordSeverSettings
from .discordinvite import discordInvite
from ..errors import notAllowed

async def discordCommands(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /discord/commands/{guild_id:\d+}
	"""
	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	if not PhaazeDiscord: return await notAllowed(cls, WebRequest, msg="Discord module is not active")

	guild_id:str = WebRequest.match_info.get("guild_id", "")
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id if guild_id.isdigit() else 0))

	if not Guild:
		return await discordInvite(cls, WebRequest, msg=f"Phaaze is not on this Server", guild_id=guild_id)

	GuildSettings:DiscordServerSettings = await getDiscordSeverSettings(cls.Web.BASE.Discord, guild_id, prevent_new=True)

	currency_name:str = GuildSettings.currency_name if GuildSettings.currency_name else cls.Web.BASE.Vars.DEFAULT_DISCORD_CURRENCY
	currency_name_multi:str = GuildSettings.currency_name_multi if GuildSettings.currency_name_multi else cls.Web.BASE.Vars.DEFAULT_DISCORD_CURRENCY_MULTI

	DiscordCommand:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Discord/commands.html")
	DiscordCommand.replace(
		guild_name = html.escape(Guild.name),
		guild_id = str(Guild.id),
		guild_currency = currency_name,
		guild_currency_multi = currency_name_multi
	)

	site:str = cls.HTMLRoot.replace(
		replace_empty = True,

		title = f"Phaaze | Discord - Commands: {Guild.name}",
		header = getNavbar(active="discord"),
		main = DiscordCommand
	)

	return cls.response(
		body=site,
		status=200,
		content_type='text/html'
	)
