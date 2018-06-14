#BASE.modules.Twitch_IRC

import asyncio
import twitch_irc as twitch

#BASE.twitch
class Init_twitch(twitch.Client):
	def __init__(self, BASE):
		self.BASE = BASE
		super().__init__()

	async def on_ready(self):
		self.BASE.is_ready.twitch = True
		self.BASE.modules.Console.GREEN("SUCCESS", "Twitch IRC Connected")
		await self.join_channel(self.nickname)
		await self.join_channel("the__cj")

	#message management
	async def on_message(self, message):
		if message.name.lower() == "phaazebot": return

		if not self.BASE.is_ready.twitch: return
		#if message.author is a BOT: return

		await self.BASE.modules._Twitch_.Base.on_message(self.BASE, message)



