from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.main_web import PhaazebotWeb

import discord
from aiohttp.web import Response
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.htmlformatter import HTMLFormatter
from Platforms.Web.index import PhaazeWebIndex
from Platforms.Web.utils import getNavbar

@PhaazeWebIndex.get("/discord/view/{guild_id:\d}")
async def discordView(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /discord/view/{guild_id:\d}
	"""
	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	if not PhaazeDiscord:
		return await cls.Tree.errors.notAllowed(cls, WebRequest, msg="Discord module is not active")

	guild_id:str = WebRequest.match_info.get("guild_id", "")
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id))

	if not Guild:
		return await cls.Tree.Discord.discordinvite.discordInvite(WebRequest, msg=f"Phaaze is not on this Server", guild_id=guild_id)

	ViewPage:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Discord/view.html")
	ViewPage.replace(
		guild_id=Guild.id,
		guild_icon_url=Guild.icon_url,
		guild_name=Guild.name
	)

	site:str = cls.HTMLRoot.replace(
		replace_empty=True,

		title="Phaaze | Discord - View",
		header=getNavbar(active="discord"),
		main=ViewPage
	)

	return cls.response(
		body=site,
		status=200,
		content_type='text/html'
	)
