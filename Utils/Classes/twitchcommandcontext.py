from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
	from Platforms.Twitch.main_twitch import PhaazebotTwitch

import twitch_irc
from Platforms.Twitch.db import getTwitchChannelCommands
from Utils.Classes.twitchcommand import TwitchCommand
from Utils.Classes.twitchchannelsettings import TwitchChannelSettings

class TwitchCommandContext(object):
	"""
	This Class acts as a holder for initial message and the ChannelSettings.
	Also has a part function. (Because i know, if i don't have it here i will do it in 50 places and forgot i did it and do it again. LULW)
	And this class is used to get the command class that should be executed.
	"""
	def __init__(self, cls:"PhaazebotTwitch", Message:twitch_irc.Message, Settings:TwitchChannelSettings=None):
		self.Twitch:"PhaazebotTwitch" = cls
		self.Message:twitch_irc.Message = Message

		self.found:bool = False
		self.Command:Optional[TwitchCommand] = None
		self.ChannelSettings:TwitchChannelSettings = Settings
		self.parts:list = Message.content.split()

	def part(self, pos:int) -> Optional[str]:
		try:
			return self.parts[pos]
		except:
			return None

	async def check(self, pos:int=0) -> bool:

		trigger:str = self.part(pos)
		if not trigger: return False

		result:list = await getTwitchChannelCommands(self.Twitch, self.Message.room_id, trigger=trigger)

		if result:
			self.found = True

		else:
			return False

		# it should always be only one entry in the list... i hope
		self.Command = result[0]

		return True
