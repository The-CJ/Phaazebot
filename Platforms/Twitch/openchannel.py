from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
	from Platforms.Twitch.main_twitch import PhaazebotTwitch

import twitch_irc

from Utils.Classes.twitchchannelsettings import TwitchChannelSettings
from Platforms.Twitch.db import getTwitchChannelSettings, getTwitchChannelUsers

async def openChannel(cls:"PhaazebotTwitch", Message:twitch_irc.Message) -> None:

	# Base: get channel settings
	ChannelSettings:TwitchChannelSettings = await getTwitchChannelSettings(cls, Message)

	# Base: get user entry
	TwitchUser:TwitchChannelSettings = None
	user_res:List[TwitchUser] = await getTwitchChannelUsers(cls, Message.room_id, user_id=Message.user_id)
	if user_res: TwitchUser = user_res.pop(0)
