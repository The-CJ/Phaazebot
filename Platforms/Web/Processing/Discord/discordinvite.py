from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.index import WebIndex

import discord
from aiohttp.web import Response, Request
from Utils.Classes.htmlformatter import HTMLFormatter
from Platforms.Web.utils import getNavbar
from ..errors import notAllowed

async def discordInvite(cls:"WebIndex", WebRequest:Request, msg:str="", guild_id:str="") -> Response:
	"""
		Default url: /discord/invite
	"""
	PhaazeDiscord:"PhaazebotDiscord" = cls.Web.BASE.Discord
	if not PhaazeDiscord: return await notAllowed(cls, WebRequest, msg="Discord module is not active")

	guild_id:str = WebRequest.query.get("guild", guild_id)
	Perm:discord.Permissions = discord.Permissions(permissions=8)
	Guild:discord.Object = discord.Object(id=guild_id)
	invite_link:str = discord.utils.oauth_url(cls.Web.BASE.Vars.DISCORD_BOT_ID, permissions=Perm, guild=Guild, redirect_uri=None)

	InvitePage:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Discord/invite.html")
	InvitePage.replace(
		invite_link = invite_link,
		msg = msg
	)

	site:str = cls.HTMLRoot.replace(
		replace_empty = True,

		title = "Phaaze | Discord - Invite",
		header = getNavbar(active="discord"),
		main = InvitePage
	)

	return cls.response(
		body=site,
		status=200,
		content_type='text/html'
	)
