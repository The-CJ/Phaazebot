from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from main import Phaazebot

import asyncio
from Platforms.Twitch.api import getTwitchStreams

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
		self._refresh_time:int = 50
		self._refresh_time_multi:float = 1.0

	def stop(self) -> None:
		if not self.running: raise Exception("not running")
		self.running = False

	async def start(self) -> None:
		if self.running: raise Exception("already running")
		self.running = True
		self.BASE.Logger.info("Started Twitch Events")

		while self.running and self.BASE.Active.twitch_events:
			self.BASE.Logger.debug("Running new twitch event check...", require="twitch:events")

			self._refresh_time_multi = 1.0 # this can get changed in a check cycle, because of crashes or, null results
			await self.check()

			await asyncio.sleep( self.delay )

	@property
	def delay(self) -> int:
		return int(self._refresh_time * self._refresh_time_multi)

	async def check(self) -> None:
			# to reduce twitch requests as much as possible, we only ask channels,
			# that have at least one discord channel alert or have Phaaze in the twitch channel active
			res:list = self.BASE.PhaazeDB.selectQuery("""
				SELECT DISTINCT
				  `twitch_channel`.`channel_id` AS `channel_id`
				FROM `twitch_channel`
				WHERE `twitch_channel`.`managed` = 1
				UNION DISTINCT
				SELECT DISTINCT
				  `discord_twitch_alert`.`twitch_channel_id` AS `channel_id`
				FROM `discord_twitch_alert`"""
			)

			if not res:
				# no alerts at all, skip everything and try again much later
				# this will happen close to never
				self._refresh_time_multi = 10.0
				self.BASE.Logger.debug(f"No actions, delaying next check ({self.delay}s)", require="twitch:events")
				return

			try:
				id_list:list = [ x["channel_id"] for x in res ]
				current_live_streams:list = await getTwitchStreams(self.BASE, id_list)

				if not current_live_streams:
					self.BASE.PhaazeDB.updateQuery( table="twitch_channel", content=dict(live=0), where="1=1" )
					self.BASE.Logger.debug(f"No channels live, delaying next check ({self.delay}s)", require="twitch:events")
					return

			except:
				# No API response
				# nothing usual, just twitch things
				self._refresh_time_multi = 0.75
				self.BASE.Logger.error(f"(Twitch Events) No Twitch API Response, delaying next check ({self.delay}s)")
				return

			# TODO: make stuff i guess
