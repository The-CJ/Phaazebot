from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Twitch.main_twitch import PhaazebotTwitch

import twitch_irc

from Utils.Classes.twitchchannelsettings import TwitchChannelSettings
from Platforms.Twitch.db import getTwitchChannelSettings

async def openChannel(cls:"PhaazebotTwitch", Message:twitch_irc.Message) -> None:

	# Base: get channel settings
	ChannelSettings:TwitchChannelSettings = await getTwitchChannelSettings(cls, Message)
