from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

import discord
from Platforms.Discord.db import getDiscordServerCommands
from Utils.Classes.discordcommand import DiscordCommand
from Utils.Classes.discordserversettings import DiscordServerSettings

class DiscordCommandContext(object):
	"""
	This Class acts as a holder for inital message and the ServerSettings.
	Also has a part function. (Because i know, if i don't have it here i will do it in 50 places and forgot i did it and do it again. LULW)
	And this class is used to get the command class that should be executed.
	"""
	def __init__(self, cls:"PhaazebotDiscord", Message:discord.Message, Settings:DiscordServerSettings=None):
		self.Discord:"PhaazebotDiscord" = cls
		self.Message:discord.Message = Message

		self.found:bool = False
		self.Command:DiscordCommand = None
		self.ServerSettings:DiscordServerSettings = Settings
		self.parts:list = Message.content.split()

	def part(self, pos:int) -> str or None:
		try:
			return self.parts[pos]
		except:
			return None

	async def check(self, pos:int=0) -> bool:

		trigger:str = self.part(pos)
		if not trigger: return False

		result:list = await getDiscordServerCommands(self.Discord, self.Message.guild.id, trigger=trigger)

		if result:
			self.found = True

		else:
			return False

		# it should always be only one entry in the list... i hope
		self.Command = result[0]

		return True
