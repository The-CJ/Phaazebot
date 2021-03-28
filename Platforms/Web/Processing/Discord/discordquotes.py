from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.main_web import PhaazebotWeb

import discord
import html
from aiohttp.web import Response
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.htmlformatter import HTMLFormatter
from Platforms.Web.index import PhaazeWebIndex
from Platforms.Web.utils import getNavbar

@PhaazeWebIndex.get("/discord/quotes/{guild_id:\d+}")
async def discordQuotes(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /discord/quotes/{guild_id:\d+}
	"""
	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	if not PhaazeDiscord:
		return await cls.Tree.errors.notAllowed(cls, WebRequest, msg="Discord module is not active")

	guild_id:str = WebRequest.match_info.get("guild_id", "")
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id if guild_id.isdigit() else 0))

	if not Guild:
		return await cls.Tree.Discord.discordinvite.discordInvite(cls, WebRequest, msg=f"Phaaze is not on this Server", guild_id=guild_id)

	DiscordQuote:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Discord/quotes.html")
	DiscordQuote.replace(
		guild_name=html.escape(Guild.name),
		guild_id=str(Guild.id),
	)

	site:str = cls.HTMLRoot.replace(
		replace_empty=True,

		title=f"Phaaze | Discord - Quotes: {Guild.name}",
		header=getNavbar(active="discord"),
		main=DiscordQuote
	)

	return cls.response(
		body=site,
		status=200,
		content_type='text/html'
	)
