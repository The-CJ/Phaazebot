from typing import TYPE_CHECKING, List
if TYPE_CHECKING:
	from Platforms.Twitch.main_twitch import PhaazebotTwitch

import twitch_irc

from Utils.Classes.twitchchannelsettings import TwitchChannelSettings
from Platforms.Twitch.db import getTwitchChannelSettings, getTwitchChannelUsers
from Platforms.Twitch.blacklist import checkBlacklist

async def openChannel(cls:"PhaazebotTwitch", Message:twitch_irc.Message) -> None:

	# Base: get channel settings
	ChannelSettings:TwitchChannelSettings = await getTwitchChannelSettings(cls, Message)

	# Base: get user entry
	TwitchUser:TwitchChannelSettings = None
	user_res:List[TwitchUser] = await getTwitchChannelUsers(cls, Message.room_id, user_id=Message.user_id)
	if user_res: TwitchUser = user_res.pop(0)

	# Blacklist: only run blacklist module if links are banned or at least on entry on the blacklist
	if ChannelSettings.blacklist_ban_links or ChannelSettings.blacklist_blacklistwords:
		executed_punishment:bool = await checkBlacklist(cls, Message, ChannelSettings, TwitchUser)
		if executed_punishment:
			cls.BASE.Logger.debug(f"(Twitch) executed blacklist punishment channel={Message.room_id}", require="twitch:blacklist")
			return

	# Anti-Spam: TODO

	# Commands: check if message triggered a command

	# Level: only execute if its a new message and its not a command
