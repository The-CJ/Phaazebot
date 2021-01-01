from typing import TYPE_CHECKING, List, Optional
if TYPE_CHECKING:
	from Platforms.Twitch.main_twitch import PhaazebotTwitch

import twitch_irc
from Utils.Classes.twitchchannelsettings import TwitchChannelSettings
from Utils.Classes.twitchuserstats import TwitchUserStats
from Platforms.Twitch.db import getTwitchChannelSettings, getTwitchChannelUsers
from Platforms.Twitch.punish import checkPunish
from Platforms.Twitch.commands import checkCommands
from Platforms.Twitch.levels import checkLevel
from Platforms.Twitch.ownchannel import clientNameChannel

async def openChannel(cls:"PhaazebotTwitch", Message:twitch_irc.Message) -> None:

	# special handling for messages in the bot channel
	if Message.room_name.lower() == cls.nickname.lower():
		return await clientNameChannel(cls, Message)

	# Base: get channel settings
	ChannelSettings:TwitchChannelSettings = await getTwitchChannelSettings(cls, Message)

	# Base: get user entry
	TwitchUser:Optional[TwitchUserStats] = None
	user_res:List[TwitchUserStats] = await getTwitchChannelUsers(cls, Message.room_id, user_id=Message.user_id)
	if user_res: TwitchUser = user_res.pop(0)

	# Protection: runs word blacklist, links, caps, spam, emotes, etc
	executed_punishment:bool = await checkPunish(cls, Message, ChannelSettings, TwitchUser)
	if executed_punishment:
		cls.BASE.Logger.debug(f"(Twitch) executed punishment on channel={Message.room_id}", require="twitch:punish")
		return

	# Commands: check if message triggered a command
	executed_command:bool = await checkCommands(cls, Message, ChannelSettings, TwitchUser)

	# Level: only execute if its a new message and its not a command
	if not executed_command:
		await checkLevel(cls, Message, ChannelSettings, TwitchUser)
