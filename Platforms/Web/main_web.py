from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from main import Phaazebot

class PhaazebotWeb(object):
	def __init__(self, BASE:"Phaazebot"):
		self.BASE:"Phaazebot" = BASE
