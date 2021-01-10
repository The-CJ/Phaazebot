from typing import List, Optional
import discord
import Platforms.Discord.const as DiscordConst
from Utils.Classes.discorduserstats import DiscordUserStats

class DiscordPermission(object):
	"""
	Given a Discord message, it gives out a requirement level for the message author.
	It has nothing to do with the discord.permissions object, which is used for discord features,
	like uploading stuff, reading messages or joining voice channels.

	This is purely for Phaaze.
	The number represents a level:
	0 - Everyone
	1 - Booster
	2 - Regulars
	3 - Mods
	4 - Server Owner
	5+  System (NOTE: don't know what it means... maybe developer debug only?)
	"""
	def __init__(self, Message:discord.Message, Member:DiscordUserStats):
		self.rank = DiscordConst.REQUIRE_EVERYONE

		if Message.author.premium_since is not None: # should mean its a discord boost... right?
			self.rank = DiscordConst.REQUIRE_BOOST

		if Member and Member.regular:
			self.rank = DiscordConst.REQUIRE_REGULAR

		if self.checkRoles(Message.author.roles):
			self.rank = DiscordConst.REQUIRE_MOD

		if Message.author == Message.guild.owner:
			self.rank = DiscordConst.REQUIRE_OWNER

	@staticmethod
	def checkRoles(has_roles:List[discord.Role], need_roles:Optional[List[str]] = None) -> bool:
		"""
		Check's if `has_roles` has at least one name hit in `need_roles`

		Default `need_roles` = ["admin", "mod", "moderator", "bot commander"]
		"""
		if need_roles is None: need_roles = ["admin", "mod", "moderator", "bot commander"]

		for Role in has_roles:
			role_name:str = Role.name.lower()

			if role_name in need_roles: return True

		return False
