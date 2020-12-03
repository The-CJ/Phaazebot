from typing import TYPE_CHECKING, Dict
if TYPE_CHECKING:
	from Platforms.Twitch.main_twitch import PhaazebotTwitch

import asyncio
import twitch_irc
from Utils.Classes.twitchchannelsettings import TwitchChannelSettings
from Utils.Classes.twitchuserstats import TwitchUserStats

class GTLMCS():
	"""
	you know what this is, just look on the discord couterpart.
	This here is the "Global Twitch Level Message Cooldown Storage"
	"""
	def __init__(self):
		self.in_cooldown:Dict[str, bool] = {}

	def check(self, Message:twitch_irc.Message) -> bool:
		user_key:str = f"{Message.room_id}-{Message.user_id}"
		if self.in_cooldown.get(user_key, None): return True
		else: return False

	def cooldown(self, cls:"PhaazebotTwitch", Message:twitch_irc.Message) -> None:
		asyncio.ensure_future(self.cooldownCoro(cls, Message))

	async def cooldownCoro(self, cls:"PhaazebotTwitch", Message:twitch_irc.Message) -> None:
		user_key:str = f"{Message.room_id}-{Message.user_id}"
		if self.in_cooldown.get(user_key, None): return

		# add
		self.in_cooldown[user_key] = True

		# wait
		await asyncio.sleep(cls.BASE.Limit.discord_level_cooldown)

		# remove
		self.in_cooldown.pop(user_key, None)

GTLMCS = GTLMCS()

async def checkLevel(cls:"PhaazebotTwitch", Message:twitch_irc.Message, ChannelSettings:TwitchChannelSettings, TwitchUser:TwitchUserStats) -> None:
	"""
	Run every time a user writes a message and updates the exp.
	"""
