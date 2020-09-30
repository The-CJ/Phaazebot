from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from main import Phaazebot

import osu_irc

class PhaazebotOsu(osu_irc.Client):
	def __init__(self, BASE:"Phaazebot", *args:list, **kwargs:dict):
		super().__init__(*args, **kwargs)
		self.BASE:"Phaazebot" = BASE

	def __bool__(self):
		return self.BASE.IsReady.osu

	async def onReady(self):
		self.BASE.Logger.info("osu! connected")
		self.BASE.IsReady.osu = True

	async def onMessage(self, Message:osu_irc.Message):
		pass
