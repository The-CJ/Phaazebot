import twitch_irc
from Utils.Classes.twitchuserstats import TwitchUserStats

class TwitchPermission(object):
	"""
	Given a Twitch message and user data from the database, it gives out a requirement level for the message author.

	The number represets a level:
	0 - Everyone
	1 - Subs
	2 - VIP
	3 - Regular
	4 - Mods
	5 - Broadcaster
	6 - Global Mod, Admin, Staff
	7+  System (NOTE: don't know what it means... maybe developer debug only?)
	"""
	def __init__(self, Message:twitch_irc.Message, User:TwitchUserStats):
		self.rank = 0

		if Message.subscriber:
			self.rank = 1

		if Message.vip:
			self.rank = 2

		if User and User.regular:
			self.rank = 3

		if Message.mod:
			self.rank = 4

		if Message.hasBadge(Message.badges, "broadcaster"):
			self.rank = 5

		if Message.hasBadge(Message.badges, "admin"): self.rank = 6
		if Message.hasBadge(Message.badges, "staff"): self.rank = 6
		if Message.hasBadge(Message.badges, "global-mod"): self.rank = 6
