from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.index import WebIndex

import discord
import html
from aiohttp.web import Response, Request
from Utils.Classes.htmlformatter import HTMLFormatter
from Platforms.Web.utils import getNavbar
from .discordinvite import discordInvite
from ..errors import notAllowed

async def discordQuotes(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /discord/quotes/{guild_id:\d+}
	"""
	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	if not PhaazeDiscord: return await notAllowed(cls, WebRequest, msg="Discord module is not active")

	guild_id:str = WebRequest.match_info.get("guild_id", "")
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id if guild_id.isdigit() else 0))

	if not Guild:
		return await discordInvite(cls, WebRequest, msg=f"Phaaze is not on this Server", guild_id=guild_id)

	DiscordCommand:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Discord/quotes.html")
	DiscordCommand.replace(
		guild_name = html.escape(Guild.name),
		guild_id = str(Guild.id),
	)

	site:str = cls.HTMLRoot.replace(
		replace_empty = True,

		title = f"Phaaze | Discord - Quotes: {Guild.name}",
		header = getNavbar(active="discord"),
		main = DiscordCommand
	)

	return cls.response(
		body=site,
		status=200,
		content_type='text/html'
	)
