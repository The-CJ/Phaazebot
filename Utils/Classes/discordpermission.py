import discord
from Utils.Classes.discorduserstats import DiscordUserStats

class DiscordPermission(object):
	"""
	Given a Discord message, it gives out a requirement level for the message author.
	It has nothing to do with the discord.permissions object, which is used for discord features,
	like uploading stuff, reading messages or joining voice channels.

	This is purly for Phaaze.
	The number represets a level:
	0 - Everyone
	1 - Booster
	2 - Regulars
	3 - Mods
	4 - Server Owner
	5+  System (NOTE: don't know what it means... maybe developer debug only?)
	"""
	def __init__(self, Message:discord.Message, Member:DiscordUserStats):
		self.rank = 0

		if Message.author.premium_since != None: # should mean its a discord boost... right?
			self.rank = 1

		if Member and Member.regular:
			self.rank = 2

		if self.checkRoles(Message.author.roles):
			self.rank = 3

		if Message.author == Message.guild.owner:
			self.rank = 4

	def checkRoles(self, roles:list, to_check:list = ["admin" ,"mod" ,"bot commander"]) -> bool:
		for Role in roles:
			user_role:str = Role.name.lower()

			for allowed_role in to_check:
				if allowed_role in user_role: return True

		return False
