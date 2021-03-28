from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.main_web import PhaazebotWeb

import discord
from aiohttp.web import Response
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.htmlformatter import HTMLFormatter
from Platforms.Web.index import PhaazeWebIndex
from Platforms.Web.utils import getNavbar

@PhaazeWebIndex.get("/discord/invite")
async def discordInvite(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, msg:str="", guild_id:str="") -> Response:
	"""
	Default url: /discord/invite
	"""
	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	if not PhaazeDiscord:
		return await cls.Tree.errors.notAllowed(cls, WebRequest, msg="Discord module is not active")

	guild_id:str = WebRequest.query.get("guild", guild_id)
	Perm:discord.Permissions = discord.Permissions(permissions=8)
	Guild:Union[discord.Object, discord.Guild] = discord.Object(id=guild_id)
	invite_link:str = discord.utils.oauth_url(cls.BASE.Vars.discord_bot_id, permissions=Perm, guild=Guild, redirect_uri='')

	InvitePage:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Discord/invite.html")
	InvitePage.replace(
		invite_link=invite_link,
		msg=msg
	)

	site:str = cls.HTMLRoot.replace(
		replace_empty=True,

		title="Phaaze | Discord - Invite",
		header=getNavbar(active="discord"),
		main=InvitePage
	)

	return cls.response(
		body=site,
		status=200,
		content_type='text/html'
	)
