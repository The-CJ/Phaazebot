from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.main_web import PhaazebotWeb

import discord
import html
from aiohttp.web import Response
from Utils.Classes.discordserversettings import DiscordServerSettings
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.htmlformatter import HTMLFormatter
from Platforms.Discord.db import getDiscordSeverSettings
from Platforms.Web.utils import getNavbar
from Platforms.Web.index import PhaazeWebIndex

@PhaazeWebIndex.get("/discord/levels/{guild_id:\d+}")
async def discordLevels(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /discord/levels/{guild_id:\d+}
	"""
	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	if not PhaazeDiscord:
		return await cls.Tree.errors.notAllowed(cls, WebRequest, msg="Discord module is not active")

	guild_id:str = WebRequest.match_info.get("guild_id", "")
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id if guild_id.isdigit() else 0))

	if not Guild:
		return await cls.Tree.Discord.discordinvite.discordInvite(cls, WebRequest, msg=f"Phaaze is not on this Server", guild_id=guild_id)

	GuildSettings:DiscordServerSettings = await getDiscordSeverSettings(PhaazeDiscord, guild_id, prevent_new=True)

	currency_name:str = GuildSettings.currency_name if GuildSettings.currency_name else cls.BASE.Vars.default_discord_currency
	currency_name_multi:str = GuildSettings.currency_name_multi if GuildSettings.currency_name_multi else cls.BASE.Vars.default_discord_currency_multi

	DiscordLevels:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Discord/levels.html")
	DiscordLevels.replace(
		guild_name=html.escape(Guild.name),
		guild_id=str(Guild.id),
		guild_currency=currency_name,
		guild_currency_multi=currency_name_multi
	)

	site:str = cls.HTMLRoot.replace(
		replace_empty=True,

		title=f"Phaaze | Discord - levels: {Guild.name}",
		header=getNavbar(active="discord"),
		main=DiscordLevels
	)

	return cls.response(
		body=site,
		status=200,
		content_type='text/html'
	)
