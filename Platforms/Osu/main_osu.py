from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from main import Phaazebot

import asyncio
import osu_irc as osu

class PhaazeOsu(osu.Client):
	def __init__(self, BASE):
		super().__init__()
		self.BASE:"Phaazebot" = BASE

	async def on_ready(self):
		self.BASE.Logger.info("osu! connected")
		self.BASE.IsReady.osu = True

	async def on_message(self, message):
		pass

	async def start(self, *a, **b):
		self.BASE.Logger.critical("TODO: FIX OSU")
		await asyncio.sleep(6000)
