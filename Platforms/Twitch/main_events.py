from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from main import Phaazebot

class PhaazebotTwitchEvents():
	"""
		This Module is to keep track of all events related to twitch
		and is a info point for other modules so we can reduce twitch api calls as much as possible.
		Under events fall:
			- twitch alerts
				- a channel going live
				- a channel goes offline
			- twitch viewer time increase
	"""
	def __init__(self, BASE):
		self.BASE:"Phaazebot" = BASE
		self.running:bool = False

	def stop(self) -> None:
		if not self.running: raise Exception("not running")
		self.running = False

	async def start(self) -> None:
		if self.running: raise Exception("already running")
		self.running = True
