from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
	from Platforms.Twitch.main_twitch import PhaazebotTwitch
	from Platforms.Web.main_web import PhaazebotWeb

import twitch_irc
from aiohttp.web import Response
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.htmlformatter import HTMLFormatter
from Platforms.Web.index import PhaazeWebIndex
from Platforms.Web.utils import getNavbar

@PhaazeWebIndex.get("/twitch/invite")
async def twitchInvite(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, msg:str="", channel_id:str="") -> Response:
	"""
	Default url: /twitch/invite
	"""
	PhaazeTwitch:"PhaazebotTwitch" = cls.BASE.Twitch
	if not PhaazeTwitch:
		return await cls.Tree.errors.notAllowed(cls, WebRequest, msg="Twitch module is not active")

	InvitePage:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Twitch/invite.html")
	InvitePage.replace(
		msg=msg,
		channel_id=channel_id,
	)

	site:str = cls.HTMLRoot.replace(
		replace_empty=True,

		title="Phaaze | Twitch - Invite",
		header=getNavbar(active="twitch"),
		main=InvitePage
	)

	return cls.response(
		body=site,
		status=200,
		content_type='text/html'
	)
