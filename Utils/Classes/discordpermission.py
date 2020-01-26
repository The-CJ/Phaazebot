import discord

class DiscordPermission(object):
	"""
		Given a Discord message, it gives out a requirement level for the message author.
		It has nothing to do with the discord.permissions object, which is used for discord features,
		like uploading stuff, reading messages or joining voice channels.

		This is purly for Phaaze.
		The number represets a level:
		0 - Everyone
		1 - Regulars (TODO: implement this)
		2 - Mods
		3 - Server Owner
		4+  System (NOTE: don't know what it means... maybe developer debug only?)
	"""
	def __init__(self, Message:discord.Message):
		self.rank = 0

		if self.checkRoles(Message.author.roles):
			self.rank = 2

		if Message.author == Message.guild.owner:
			self.rank = 3

	def checkRoles(self, roles:list, to_check:list = ["admin" ,"mod" ,"bot commander"]) -> bool:
		for Role in roles:
			user_role:str = Role.name.lower()

			for allowed_role in to_check:
				if allowed_role in user_role: return True

		return False
