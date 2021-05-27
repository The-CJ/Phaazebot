from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
	from Platforms.Twitch.main_twitch import PhaazebotTwitch
	from Platforms.Web.main_web import PhaazebotWeb

import twitch_irc
import html
from aiohttp.web import Response
from Utils.Classes.authtwitchwebuser import AuthTwitchWebUser
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.htmlformatter import HTMLFormatter
from Platforms.Web.utils import getNavbar, authTwitchWebUser
from Platforms.Web.index import PhaazeWebIndex

@PhaazeWebIndex.get("/twitch/dashboard/{channel_id:\d+}")
async def twitchDashboard(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /twitch/dashboard/{channel_id:\d+}
	"""
	PhaazeTwitch:"PhaazebotTwitch" = cls.BASE.Twitch
	if not PhaazeTwitch:
		return await cls.Tree.errors.notAllowed(cls, WebRequest, msg="Twitch module is not active")

	channel_id:str = WebRequest.match_info.get("channel_id", "")
	PhaazeTwitch.getChannel()
	Channel:Optional[twitch_irc.Channel] = PhaazeTwitch.getChannel(channel_id=channel_id)

	if not Channel:
		return await cls.Tree.errors.notFound(cls, WebRequest, msg=f"Twitch Channel not found...")

	AuthTwitch:AuthTwitchWebUser = await authTwitchWebUser(cls, WebRequest)
	if not AuthTwitch.found:
		return await cls.Tree.Discord.twitchlogin.twitchLogin(cls, WebRequest)

	# TODO

	CheckMember:discord.Member = Channel.get_member(int(AuthTwitch.User.user_id))
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
		guild_name=html.escape(Channel.name),
		guild_id=Channel.id,
		web_root=cls.BASE.Vars.web_root
	)

	site:str = cls.HTMLRoot.replace(
		replace_empty=True,

		title=f"Phaaze | Discord - Dashboard: {Channel.name}",
		header=getNavbar(active="discord"),
		main=DiscordDash
	)

	return cls.response(
		body=site,
		status=200,
		content_type='text/html'
	)
