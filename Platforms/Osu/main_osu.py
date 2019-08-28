from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from main import Phaazebot

import osu_irc as osu

class PhaazeOsu(osu.Client):
	def __init__(self, BASE):
		super().__init__()
		self.BASE:"Phaazebot" = BASE

	async def onReady(self):
		self.BASE.Logger.info("osu! connected")
		self.BASE.IsReady.osu = True

	async def onMessage(self, message):
		print(message)
