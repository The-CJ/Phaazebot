from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from main import Phaazebot

import osu_irc as osu

class PhaazebotOsu(osu.Client):
	def __init__(self, BASE):
		super().__init__()
		self.BASE:"Phaazebot" = BASE

	def __bool__(self):
		return self.BASE.IsReady.osu

	async def onReady(self):
		self.BASE.Logger.info("osu! connected")
		self.BASE.IsReady.osu = True

	async def onMessage(self, message):
		pass
