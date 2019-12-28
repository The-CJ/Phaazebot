from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from main import Phaazebot

class PhaazebotTwitchAlerts():
	def __init__(self, BASE):
		self.BASE:"Phaazebot" = BASE

	def __bool__(self):
		return self.BASE.IsReady.osu
