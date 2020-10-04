from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Twitch.main_twitch import PhaazebotTwitch

import twitch_irc
# import re
# from Utils.regex import ContainsLink
from Utils.Classes.twitchchannelsettings import TwitchChannelSettings
from Utils.Classes.twitchuserstats import TwitchUserStats
from Utils.Classes.twitchpermission import TwitchPermission

async def checkBlacklist(cls:"PhaazebotTwitch", Message:twitch_irc.Message, ChannelSettings:TwitchChannelSettings, DiscordUser:TwitchUserStats) -> bool:

	PhaazePermissions:twitch_irc.UserState = Message.Channel.me

	# if the bot cant do anything or the author is a regular or higher, skip checks
	if not PhaazePermissions.mod: return False
	if Message: pass
	if TwitchPermission(Message, DiscordUser).rank >= 2: return False

	# if this is True after all checks => punish
	punish:bool = False
	reason:str = None

	# links are not allowed
	if ChannelSettings.blacklist_ban_links:
		punish = await checkBanLinks(cls, Message, ChannelSettings)
		reason = "ban-links"

	if ChannelSettings.blacklist_blacklistwords and not punish:
		punish = await checkWordBlacklist(cls, Message, ChannelSettings)
		reason = "word-blacklist"

	if punish:
		await executePunish(cls, Message, ChannelSettings, reason=reason)
		return True

	else:
		return False

async def checkBanLinks(cls:"PhaazebotTwitch", Message:twitch_irc.Message, ChannelSettings:TwitchChannelSettings) -> bool:
	pass

async def checkWordBlacklist(cls:"PhaazebotTwitch", Message:twitch_irc.Message, ChannelSettings:TwitchChannelSettings) -> bool:
	pass

async def executePunish(cls:"PhaazebotTwitch", Message:twitch_irc.Message, ChannelSettings:TwitchChannelSettings, reason:str = None) -> None:
	pass
