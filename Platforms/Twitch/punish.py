from typing import TYPE_CHECKING, Iterator, Optional, Dict
if TYPE_CHECKING:
	from Platforms.Twitch.main_twitch import PhaazebotTwitch

import asyncio
import twitch_irc
import re
import Platforms.Twitch.const as TwitchConst
from Utils.regex import ContainsLink
from Utils.Classes.twitchchannelsettings import TwitchChannelSettings
from Utils.Classes.twitchuserstats import TwitchUserStats
from Utils.Classes.twitchpermission import TwitchPermission
from Platforms.Twitch.logging import loggingOnModerationTimeout, loggingOnModerationBan

class GlobalTwitchTimeoutRememberStorage(object):
	"""
	and now the "Global Twitch Timeout Remember Storage"
	just like in discord we got some storage names classes, yeah
	this one remembers what chatter is still in a "grace" period

	K see this, when someone get a reason to be timeout, phaaze first gives a
	3s timeout (aka a purge) and the user is for 160sec in a grace period.

	If the user gets timeout again then:
		Timeout = ChannelSettings.blacklist_punishment
		Grace = ChannelSettings.blacklist_punishment * 2

	getting timed out by phaaze again will be:
		Timeout = ChannelSettings.blacklist_punishment * 2
		Grace = ChannelSettings.blacklist_punishment * 3

	after that... well lets just say a shotgun is pretty cool.
	"""
	def __init__(self):
		self.in_warning:Dict[str, bool] = {}
		self.in_grace_one:Dict[str, bool] = {}
		self.in_grace_two:Dict[str, bool] = {}

	def check(self, Message:twitch_irc.Message) -> Optional[int]:
		key:str = f"{Message.room_id}-{Message.user_id}"
		if self.in_grace_two.get(key, None): return 2
		if self.in_grace_one.get(key, None): return 1
		if self.in_warning.get(key, None): return 0
		else: return None

	def grace(self, Message:twitch_irc.Message, level:Optional[int], time:int) -> None:
		asyncio.ensure_future(self.graceCoro(Message, level, time))

	async def graceCoro(self, Message:twitch_irc.Message, level:int or None, time:int) -> None:
		key:str = f"{Message.room_id}-{Message.user_id}"

		# if level is None we take the user out of everything
		if level is None:
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


GTTRS:GlobalTwitchTimeoutRememberStorage = GlobalTwitchTimeoutRememberStorage()

async def checkPunish(cls:"PhaazebotTwitch", Message:twitch_irc.Message, ChannelSettings:TwitchChannelSettings, TwitchUser:TwitchUserStats) -> bool:

	PhaazePermissions:twitch_irc.UserState = Message.Channel.me

	# if the bot can't do anything or the author is a regular or higher, skip checks
	if not PhaazePermissions.mod: return False
	if TwitchPermission(Message, TwitchUser).rank >= 2: return False

	# if this is True after all checks => punish
	punish:bool = False
	reason:Optional[str] = None

	# link option is active, check for links
	if ChannelSettings.punish_option_links:
		punish = await checkLinks(cls, Message, ChannelSettings)
		reason = "links"

	# blacklist is active, check for bad words
	if not punish and ChannelSettings.punish_option_words:
		punish = await checkBlacklist(cls, Message, ChannelSettings)
		reason = "wordblacklist"

	# huge amount of emotes
	if not punish and ChannelSettings.punish_option_emotes:
		punish = await checkEmotes(cls, Message, ChannelSettings)
		reason = "emotes"

	# huge amount of caps
	if not punish and ChannelSettings.punish_option_caps:
		punish = await checkCaps(cls, Message, ChannelSettings)
		reason = "caps"

	if punish:
		await executePunish(cls, Message, ChannelSettings, reason=reason)
		return True

	else:
		return False

# checks
async def checkBlacklist(_cls:"PhaazebotTwitch", Message:twitch_irc.Message, ChannelSettings:TwitchChannelSettings) -> bool:
	message_text:str = Message.content.lower()

	for re_pattern in ChannelSettings.punish_wordblacklist:
		try:
			if re.search(re_pattern, message_text):
				return True
		except:
			pass

	return False

async def checkLinks(_cls:"PhaazebotTwitch", Message:twitch_irc.Message, ChannelSettings:TwitchChannelSettings) -> bool:

	found_links:Iterator = re.finditer(ContainsLink, Message.content)

	if not found_links: return False

	# check all found link, by default, every link is punished
	for found_link in found_links:
		allowed = False

		# check all whitelisted link regex
		for allowed_link in ChannelSettings.punish_linkwhitelist:
			# link is whitelisted, allow it, break allowed_link search
			if re.search(allowed_link, found_link.group(0)):
				allowed = True
				break

		# link is not in whitelist
		if not allowed:
			return True

	# all links could be found in the whitelist
	return False

async def checkEmotes(_cls:"PhaazebotTwitch", Message:twitch_irc.Message, _ChannelSettings:TwitchChannelSettings) -> bool:

	# channel is in a emote only mode, user can't type normally... so we disable this check for now
	if Message.Channel.emote_only: return False

	# good question... what is a good amount of maximum emotes? 10 for now,
	# also take in consideration that this message is emote only, no text
	# maybe add a slider to set individual limit
	if Message.emote_only and Message.emote_count >= 10:
		return True

	# with text of any kind we allow 2 emote more because... duh?
	if Message.emote_count >= 12:
		return True

	return False

async def checkCaps(_cls:"PhaazebotTwitch", Message:twitch_irc.Message, _ChannelSettings:TwitchChannelSettings) -> bool:

	total:int = 0
	caps:int = 0

	for char in Message.content:
		total += 1
		if char.isupper():
			caps += 1

	# i think short CAPS words are ok
	if total < 16:
		return False

	ratio:float = caps / total
	if ratio > (2/3): # 66%
		return True

	return False

async def checkCopyPasta(_cls:"PhaazebotTwitch", _Message:twitch_irc.Message, _ChannelSettings:TwitchChannelSettings) -> bool:
	pass # TODO: yeah good idea, i will make this later

async def checkUnicode(_cls:"PhaazebotTwitch", _Message:twitch_irc.Message, _ChannelSettings:TwitchChannelSettings) -> bool:
	pass # TODO: Unicode could be extra tricky... because there is Japanese and whatever, which by definition are all unicode... hooray

# finals and utils
async def executePunish(cls:"PhaazebotTwitch", Message:twitch_irc.Message, ChannelSettings:TwitchChannelSettings, reason:str = None) -> None:
	punish_time:int = ChannelSettings.punish_timeout
	# always have a minimum cooldown
	punish_time = max(punish_time, cls.BASE.Limit.twitch_punish_time_min, TwitchConst.COMMAND_COOLDOWN_MIN)
	# but also be to long
	punish_time = min(punish_time, cls.BASE.Limit.twitch_punish_time_max, TwitchConst.COMMAND_COOLDOWN_MAX)

	current_user_state:int = GTTRS.check(Message)

	if current_user_state == 2: # user fucked up in grace_two, aka we ban now
		await cls.sendMessage(Message.room_name, f"/ban {Message.user_name}")
		await loggingOnModerationBan(cls, ChannelSettings, user_name=Message.user_name, user_id=Message.user_id, reason=reason)

	elif current_user_state == 1: # user timeout again in grace_one, double timeout and grace
		GTTRS.grace(Message, 2, punish_time * 4)
		await cls.sendMessage(Message.room_name, f"/timeout {Message.user_name} {punish_time * 2}")
		await loggingOnModerationTimeout(cls, ChannelSettings, user_name=Message.user_name, user_id=Message.user_id, reason=reason, timeout=punish_time * 2, level=2)
		await notifyMessage(cls, Message, ChannelSettings, reason, 2)

	elif current_user_state == 0: # user didn't learn from warning, timeout and grace
		GTTRS.grace(Message, 1, punish_time * 2)
		await cls.sendMessage(Message.room_name, f"/timeout {Message.user_name} {punish_time}")
		await loggingOnModerationTimeout(cls, ChannelSettings, user_name=Message.user_name, user_id=Message.user_id, reason=reason, timeout=punish_time, level=1)
		await notifyMessage(cls, Message, ChannelSettings, reason, 1)

	else: # someone did a casual oops, that's ok, give a warning
		GTTRS.grace(Message, 0, 180)
		await cls.sendMessage(Message.room_name, f"/timeout {Message.user_name} 3")
		await loggingOnModerationTimeout(cls, ChannelSettings, user_name=Message.user_name, user_id=Message.user_id, reason=reason, timeout=3, level=0)
		await notifyMessage(cls, Message, ChannelSettings, reason, 0)

DEFAULT_PUNISH_MSG_WORDS: str = "[[warn-level]] @[user-display-name], you posted a blacklisted word!"
DEFAULT_PUNISH_MSG_CAPS: str = "[[warn-level]] @[user-display-name], stop using huge amounts of CAPS!"
DEFAULT_PUNISH_MSG_COPYPASTA: str = "[[warn-level]] @[user-display-name], stop using Copy-Pasta messages!"
DEFAULT_PUNISH_MSG_EMOTES:str = "[[warn-level]] @[user-display-name], emotes are cool, too many are not!"
DEFAULT_PUNISH_MSG_LINKS:str = "[[warn-level]] @[user-display-name], stop posting links!"
DEFAULT_PUNISH_MSG_UNICODE:str = "[[warn-level]] @[user-display-name], stop using ㄩ几丨匚ㄖᗪ乇 Messages!"
DEFAULT_UNKNOWN:str = "[[warn-level]] @[user-display-name], whatever you just done, stop it!"

async def notifyMessage(cls:"PhaazebotTwitch", Message:twitch_irc.Message, ChannelSettings:TwitchChannelSettings, reason:str, level:int or None) -> None:
	if not ChannelSettings.punish_notify: return # notify messages are unwanted

	notify_msg:str = ""
	if reason == "wordblacklist":
		notify_msg = ChannelSettings.punish_msg_words or DEFAULT_PUNISH_MSG_WORDS
	elif reason == "links":
		notify_msg = ChannelSettings.punish_msg_links or DEFAULT_PUNISH_MSG_LINKS
	elif reason == "emotes":
		notify_msg = ChannelSettings.punish_msg_emotes or DEFAULT_PUNISH_MSG_EMOTES
	elif reason == "caps":
		notify_msg = ChannelSettings.punish_msg_caps or DEFAULT_PUNISH_MSG_CAPS

	if not notify_msg:
		notify_msg = DEFAULT_UNKNOWN

	if level == 1: warn_level:str = "2nd warning"
	elif level == 2: warn_level:str = "Last warning"
	else: warn_level:str = "Warning"

	notify_msg = notify_msg.replace("[warn-level]", warn_level)
	notify_msg = notify_msg.replace("[reason]", reason)
	notify_msg = notify_msg.replace("[user-name]", Message.user_name)
	notify_msg = notify_msg.replace("[user-display-name]", Message.display_name)
	notify_msg = notify_msg.replace("[user-id", Message.user_id)
	notify_msg = notify_msg.replace("[room-id", Message.room_id)
	notify_msg = notify_msg.replace("[room-name", Message.room_name)

	await cls.sendMessage(Message.room_name, notify_msg)
