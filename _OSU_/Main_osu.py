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
		self.BASE.is_ready.osu = True

	#message management
	async def on_message(self, message):
		if message.name.lower() == self.nickname.lower(): return
		if not self.BASE.is_ready.osu: return

		await self.BASE.modules._Osu_.Base.on_message(self.BASE, message)

	async def on_raw_data(self, r):
		pass
