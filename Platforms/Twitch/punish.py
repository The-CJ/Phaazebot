from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Twitch.main_twitch import PhaazebotTwitch

import asyncio
import twitch_irc
import re
# from Utils.regex import ContainsLink
from Utils.Classes.twitchchannelsettings import TwitchChannelSettings
from Utils.Classes.twitchuserstats import TwitchUserStats
from Utils.Classes.twitchpermission import TwitchPermission
from Platforms.Twitch.logging import loggingOnModerationTimeout, loggingOnModerationBan

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

DEBUG = True

async def checkPunish(cls:"PhaazebotTwitch", Message:twitch_irc.Message, ChannelSettings:TwitchChannelSettings, DiscordUser:TwitchUserStats) -> bool:

	PhaazePermissions:twitch_irc.UserState = Message.Channel.me

	# if the bot can't do anything or the author is a regular or higher, skip checks
	if not PhaazePermissions.mod and not DEBUG: return False
	if TwitchPermission(Message, DiscordUser).rank >= 2 and not DEBUG: return False

	# if this is True after all checks => punish
	punish:bool = False
	reason:str = None

	# link option is active, check for links
	if ChannelSettings.punish_option_links: # TODO: add link whitlist first
		punish = await checkLinks(cls, Message, ChannelSettings)
		reason = "links"

	# blacklist is active, check for bad words
	if not punish and ChannelSettings.punish_option_words:
		punish = await checkBlacklist(cls, Message, ChannelSettings)
		reason = "wordblacklist"

	if punish:
		await executePunish(cls, Message, ChannelSettings, reason=reason)
		return True

	else:
		return False

# checks
async def checkBlacklist(cls:"PhaazebotTwitch", Message:twitch_irc.Message, ChannelSettings:TwitchChannelSettings) -> bool:
	message_text:str = Message.content.lower()

	for re_pattern in ChannelSettings.punish_wordblacklist:
		try:
			if re.search(re_pattern, message_text):
				return True
		except:
			pass

	return False

async def checkLinks(cls:"PhaazebotTwitch", Message:twitch_irc.Message, ChannelSettings:TwitchChannelSettings) -> bool:
	pass

async def checkEmotes(cls:"PhaazebotTwitch", Message:twitch_irc.Message, ChannelSettings:TwitchChannelSettings) -> bool:
	pass

async def checkCaps(cls:"PhaazebotTwitch", Message:twitch_irc.Message, ChannelSettings:TwitchChannelSettings) -> bool:
	pass

async def checkCopyPasta(cls:"PhaazebotTwitch", Message:twitch_irc.Message, ChannelSettings:TwitchChannelSettings) -> bool:
	pass

async def checkUnicode(cls:"PhaazebotTwitch", Message:twitch_irc.Message, ChannelSettings:TwitchChannelSettings) -> bool:
	pass

# finals and utils
async def executePunish(cls:"PhaazebotTwitch", Message:twitch_irc.Message, ChannelSettings:TwitchChannelSettings, reason:str = None) -> None:
	punish_time:int = max(ChannelSettings.punish_timeout, 10) # at least 10
	current_user_state:int = GTTRS.check(Message)

	if current_user_state == 2: # user fucked up in grace_two, aka we ban now
		await cls.sendMessage(Message.room_name, f"/ban {Message.user_name}")
		await loggingOnModerationBan(cls, user_name=Message.user_name, reason=reason)

	elif current_user_state == 1: # user timeout again in grace_one, double timeout and grace
		GTTRS.grace(Message, 2, punish_time * 4)
		await cls.sendMessage(Message.room_name, f"/timeout {Message.user_name} {punish_time * 2}")
		await loggingOnModerationTimeout(cls, user_name=Message.user_name, reason=reason, timeout=punish_time, level=2)

	elif current_user_state == 0: # user didn't learn from warning, timeout and grace
		GTTRS.grace(Message, 1, punish_time * 2)
		await cls.sendMessage(Message.room_name, f"/timeout {Message.user_name} {punish_time}")
		await loggingOnModerationTimeout(cls, user_name=Message.user_name, reason=reason, timeout=punish_time, level=1)

	else: # someone did a casual oopsi, thats ok, give a warning
		GTTRS.grace(Message, 0, 180)
		await cls.sendMessage(Message.room_name, f"/timeout {Message.user_name} 3")
		await loggingOnModerationTimeout(cls, user_name=Message.user_name, reason=reason, timeout=3, level=0)

	await notifyMessage(ChannelSettings, reason, current_user_state)

DEFAULT_PUNISH_MSG_WORDS:str = "[warn-level] @[user-display-name], you posted a blacklisted word!"
DEFAULT_PUNISH_MSG_CAPS:str = "[warn-level] @[user-display-name], stop using huge amounts of CAPS!"
DEFAULT_PUNISH_MSG_COPYPASTA:str = "[warn-level] @[user-display-name], stop using Copy-Pasta messages!"
DEFAULT_PUNISH_MSG_EMOTES:str = "[warn-level] @[user-display-name], emotes are cool, too many are not!"
DEFAULT_PUNISH_MSG_LINKS:str = "[warn-level] @[user-display-name], stop posting links!"
DEFAULT_PUNISH_MSG_UNICODE:str = "[warn-level] @[user-display-name], stop using ㄩ几丨匚ㄖᗪ乇 Messages!"
DEFAULT_UNKNOWN:str = "[warn-level] @[user-display-name], whatever you just done, stop it!"

async def notifyMessage(ChannelSettings:TwitchChannelSettings, reason:str, level:int or None) -> None:
	if not ChannelSettings.punish_notify: return # notify messages are unwanted
