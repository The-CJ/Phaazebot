from typing import Optional
import twitch_irc
import Platforms.Twitch.const as TwitchConst
from Utils.Classes.twitchuserstats import TwitchUserStats

class TwitchPermission(object):
	"""
	Given a Twitch message and user data from the database, it gives out a requirement level for the message author.

	The number represents a level:
	0 - Everyone
	1 - Subs
	2 - VIP
	3 - Regular
	4 - Mods
	5 - Broadcaster
	6 - Global Mod, Admin, Staff
	7+  System (NOTE: don't know what it means... maybe developer debug only?)
	"""
	def __init__(self, Message:twitch_irc.Message, User:Optional[TwitchUserStats]):
		self.rank = TwitchConst.REQUIRE_EVERYONE

		if Message.subscriber:
			self.rank = TwitchConst.REQUIRE_SUB

		if Message.vip:
			self.rank = TwitchConst.REQUIRE_VIP

		if User and User.regular:
			self.rank = TwitchConst.REQUIRE_REGULAR

		if Message.mod:
			self.rank = TwitchConst.REQUIRE_MOD

		if Message.hasBadge(Message.badges, "broadcaster"):
			self.rank = TwitchConst.REQUIRE_OWNER

		if Message.hasBadge(Message.badges, "admin"): self.rank = TwitchConst.REQUIRE_ADMIN
		if Message.hasBadge(Message.badges, "staff"): self.rank = TwitchConst.REQUIRE_ADMIN
		if Message.hasBadge(Message.badges, "global-mod"): self.rank = TwitchConst.REQUIRE_ADMIN
