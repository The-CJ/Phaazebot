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
		return await cls.Tree.Twitch.twitchinvite.twitchInvite(cls, WebRequest, msg=f"Twitch Channel not found...", channel_id=channel_id)

	AuthTwitch:AuthTwitchWebUser = await authTwitchWebUser(cls, WebRequest)
	if not AuthTwitch.found:
		return await cls.Tree.Twitch.twitchlogin.twitchLogin(cls, WebRequest)

	TwitchDash:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Twitch/Dashboard/main.html")
	TwitchDash.replace(
		replace_empty=False
	)

	# make it twice, since some included locations also have replaceable items
	TwitchDash.replace(
		channel_name=html.escape(Channel.name),
		channel_id=Channel.channel_id,
		web_root=cls.BASE.Vars.web_root
	)

	site:str = cls.HTMLRoot.replace(
		replace_empty=True,

		title=f"Phaaze | Twitch - Dashboard: {Channel.name}",
		header=getNavbar(active="twitch"),
		main=TwitchDash
	)

	return cls.response(
		body=site,
		status=200,
		content_type='text/html'
	)
