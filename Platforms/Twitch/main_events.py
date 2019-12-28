from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from main import Phaazebot

import asyncio

class PhaazebotTwitchEvents(object):
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
		self.refresh_time:int = 50
		self.refresh_time_multi:float = 1.0

	def stop(self) -> None:
		if not self.running: raise Exception("not running")
		self.running = False

	async def start(self) -> None:
		if self.running: raise Exception("already running")
		self.running = True
		self.BASE.Logger.info("Started Twitch Events")

		while self.running and self.BASE.Active.twitch_events:
			self.BASE.Logger.debug("Running new twitch event check...", require="twitch:events")

			self.refresh_time_multi = 1.0 # this can get changed in a check cycle, because of crashes or, null results
			await self.check()

			await asyncio.sleep( self.refresh_time * self.refresh_time_multi )

	async def check(self) -> None:
		pass
