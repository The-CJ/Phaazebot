#BASE.modules.Osu_IRC

import asyncio
import osu_irc as osu

#BASE.osu
class Init_osu(osu.Client):
	def __init__(self, BASE):
		self.BASE = BASE
		super().__init__()

	async def on_ready(self):
		self.BASE.modules.Console.INFO("Osu IRC Connected")

		#join own channel
		await self.join_channel(self.nickname)

		self.BASE.is_ready.osu = True

	#message management
	async def on_message(self, message):
		if message.name.lower() == self.nickname.lower(): return
		if not self.BASE.is_ready.osu: return

	async def on_raw_data(self, r):
		pass
