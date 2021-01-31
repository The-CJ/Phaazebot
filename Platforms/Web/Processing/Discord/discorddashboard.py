from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord
	from Platforms.Web.main_web import PhaazebotWeb

import discord
import html
from aiohttp.web import Response
from Utils.Classes.authdiscordwebuser import AuthDiscordWebUser
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.htmlformatter import HTMLFormatter
from Platforms.Web.utils import getNavbar, authDiscordWebUser
from Platforms.Web.index import PhaazeWebIndex

@PhaazeWebIndex.get("/discord/dashboard/{guild_id:\d+}")
async def discordDashboard(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /discord/dashboard/{guild_id:\d+}
	"""
	PhaazeDiscord:"PhaazebotDiscord" = cls.BASE.Discord
	if not PhaazeDiscord:
		return await cls.Tree.errors.notAllowed(cls, WebRequest, msg="Discord module is not active")

	guild_id:str = WebRequest.match_info.get("guild_id", "")
	Guild:discord.Guild = discord.utils.get(PhaazeDiscord.guilds, id=int(guild_id if guild_id.isdigit() else 0))

	if not Guild:
		return await cls.Tree.Discord.discordinvite.discordInvite(cls, WebRequest, msg=f"Phaaze is not on this Server", guild_id=guild_id)

	AuthDiscord:AuthDiscordWebUser = await authDiscordWebUser(cls, WebRequest)
	if not AuthDiscord.found:
		return await cls.Tree.Discord.discordlogin.discordLogin(cls, WebRequest)

	CheckMember:discord.Member = Guild.get_member(int(AuthDiscord.User.user_id))
	if not CheckMember:
		return cls.response(status=302, headers={"Location": f"/discord/view/{guild_id}?error=no_user"})

	if not (CheckMember.guild_permissions.administrator or CheckMember.guild_permissions.manage_guild):
		return cls.response(status=302, headers={"Location": f"/discord/view/{guild_id}?error=missing_permissions"})

	DiscordDash:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Discord/Dashboard/main.html")
	DiscordDash.replace(
		location_home=HTMLFormatter("Platforms/Web/Content/Html/Discord/Dashboard/location_home.html"),
		location_quotes=HTMLFormatter("Platforms/Web/Content/Html/Discord/Dashboard/location_quotes.html"),
		location_twitch_alerts=HTMLFormatter("Platforms/Web/Content/Html/Discord/Dashboard/location_twitch_alerts.html"),
		location_regulars=HTMLFormatter("Platforms/Web/Content/Html/Discord/Dashboard/location_regulars.html"),
		location_levels=HTMLFormatter("Platforms/Web/Content/Html/Discord/Dashboard/location_levels.html"),
		location_configs_chat=HTMLFormatter("Platforms/Web/Content/Html/Discord/Dashboard/location_configs_chat.html"),
		location_configs_event=HTMLFormatter("Platforms/Web/Content/Html/Discord/Dashboard/location_configs_event.html"),
		location_configs_level=HTMLFormatter("Platforms/Web/Content/Html/Discord/Dashboard/location_configs_level.html"),
		location_configs_channel=HTMLFormatter("Platforms/Web/Content/Html/Discord/Dashboard/location_configs_channel.html"),
		location_configs_master=HTMLFormatter("Platforms/Web/Content/Html/Discord/Dashboard/location_configs_master.html"),
		location_commands_command=HTMLFormatter("Platforms/Web/Content/Html/Discord/Dashboard/location_commands_command.html"),
		location_commands_help=HTMLFormatter("Platforms/Web/Content/Html/Discord/Dashboard/location_commands_help.html"),
		location_commands_assign=HTMLFormatter("Platforms/Web/Content/Html/Discord/Dashboard/location_commands_assign.html"),
		location_logs=HTMLFormatter("Platforms/Web/Content/Html/Discord/Dashboard/location_logs.html"),
	)
	# make it twice, since some included locations also have replaceable items
	DiscordDash.replace(
		guild_name=html.escape(Guild.name),
		guild_id=Guild.id,
		web_root=cls.BASE.Vars.web_root
	)

	site:str = cls.HTMLRoot.replace(
		replace_empty=True,

		title=f"Phaaze | Discord - Dashboard: {Guild.name}",
		header=getNavbar(active="discord"),
		main=DiscordDash
	)

	return cls.response(
		body=site,
		status=200,
		content_type='text/html'
	)
