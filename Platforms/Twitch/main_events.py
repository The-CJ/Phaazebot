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
				SELECT
				  `twitch_channel`.`channel_id`,
				  `twitch_channel`.`game_id`,
				  `twitch_channel`.`live`,
				  GROUP_CONCAT(`discord_twitch_alert`.`discord_channel_id`) AS `alert_discord`
				FROM `twitch_channel`
				LEFT JOIN `discord_twitch_alert`
				  ON `discord_twitch_alert`.`twitch_channel_id` = `twitch_channel`.`channel_id`
				GROUP BY `twitch_channel`.`channel_id`"""
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

			# generate status dict's
			status_dict_db:dict = self.generateStatusDB(res)
			status_dict_api:dict = self.generateStatusAPI(current_live_streams)

			await self.checkLiveStatus(status_dict_db, status_dict_api)

			# everything done, set channels live in db
			channel_ids:str = ",".join(Chan.user_id for Chan in current_live_streams)
			self.BASE.PhaazeDB.query(f"""
				UPDATE `twitch_channel`
				SET `live` = CASE WHEN `twitch_channel`.`channel_id` IN ({channel_ids}) THEN 1 ELSE 0 END""",
			)
			self.BASE.Logger.debug("Updated twitch channel live status", require="twitch:events")

	# dict generator
	def generateStatusDB(self, db_result:list) -> dict:
		status_dict:dict = dict()

		for r in db_result:

			channel_id:str = str( r.get("channel_id", "") or "" )
			game_id:str = str( r.get("game_id", "") or "" )
			live:bool = bool( r.get("live", 0) )

			status_dict[channel_id] = dict(
				game_id = game_id,
				live = live
			)

		return status_dict

	def generateStatusAPI(self, api_result:list) -> dict:
		status_dict:dict = dict()

		for R in api_result:

			user_id:str = str( R.user_id )
			game_id:str = str( R.game_id )
			live:bool = bool( R.stream_type == "live" )

			status_dict[user_id] = dict(
				game_id = game_id,
				live = live
			)

		return status_dict

	async def checkLiveStatus(self, status_db:dict, status_api:dict) -> None:
		"""
			Checks the currently known channels stats in status_api,
			with the last known status in the status_db.

			Its easy to understand, a channel is gone offline
			if he is not in status_api but has live == True in the status_db
			and gone online when live == False but is found in the status_api
		"""

		for channel_id in status_db:

			entry_db:dict = status_db.get(channel_id, {})
			entry_api:dict = status_api.get(channel_id, {})

		pass

	# events
	async def eventLive(self) -> None:
		pass

	async def eventGamechange(self) -> None:
		pass

	async def eventOffline(self, id_list:list) -> None:
		"""
			Event thats called for all twitch channels than gone offline
			id_list is a list of channel id strings
		"""
		pass
