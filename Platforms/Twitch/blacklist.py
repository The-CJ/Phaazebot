from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Twitch.main_twitch import PhaazebotTwitch

import asyncio
import twitch_irc
# import re
# from Utils.regex import ContainsLink
from Utils.Classes.twitchchannelsettings import TwitchChannelSettings
from Utils.Classes.twitchuserstats import TwitchUserStats
from Utils.Classes.twitchpermission import TwitchPermission

class GTTRS():
	"""
	and now the "Global Twitch Timout Remember Storage"
	just like in discord we got some strage names classes, yeeeah
	this one remembers what chatter is still in a "grace" period

	K see this, when someone get a reason to be timeouted, phaaze first gives a
	3s timeout (aka a purge) and the user is for 160sec in a grace period.

	If the user gets timeouted again then:
		Timeout = ChannelSettings.blacklist_punishment
		Grace = ChannelSettings.blacklist_punishment * 2

	getting timed out by phaaze again will be:
		Timeout = ChannelSettings.blacklist_punishment * 2
		Grace = ChannelSettings.blacklist_punishment * 3

	after that... well lets just say a shotgun is pretty cool.
	"""
	def __init__(self):
		self.in_warning:dict = dict()
		self.in_grace_one:dict = dict()
		self.in_grace_two:dict = dict()

	def check(self, Message:twitch_irc.Message) -> int or None:
		key:str = f"{Message.room_id}-{Message.user_id}"
		if self.in_grace_two.get(key, None): return 2
		if self.in_grace_one.get(key, None): return 1
		if self.in_warning.get(key, None): return 0
		else: return None

	def grace(self, Message:twitch_irc.Message, level:int or None, time:int) -> None:
		asyncio.ensure_future( self.graceCoro(Message, level, time) )

	async def graceCoro(self, Message:twitch_irc.Message, level:int or None, time:int) -> None:
		key:str = f"{Message.room_id}-{Message.user_id}"

		# if level is None we take the user out of everything
		if level == None:
			self.in_warning.pop(key, None)
			self.in_grace_one.pop(key, None)
			self.in_grace_two.pop(key, None)
			return

		if level == 0:
			self.in_warning[key] = True
			await asyncio.sleep(160)
			self.in_warning.pop(key, None)

		elif level == 1:
			self.in_grace_one[key] = True
			await asyncio.sleep(time)
			self.in_grace_one.pop(key, None)

		elif level == 2:
			self.in_grace_two[key] = True
			await asyncio.sleep(time)
			self.in_grace_two.pop(key, None)

GTTRS = GTTRS()

async def checkBlacklist(cls:"PhaazebotTwitch", Message:twitch_irc.Message, ChannelSettings:TwitchChannelSettings, DiscordUser:TwitchUserStats) -> bool:

	PhaazePermissions:twitch_irc.UserState = Message.Channel.me

	# if the bot cant do anything or the author is a regular or higher, skip checks
	if not PhaazePermissions.mod: return False
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
