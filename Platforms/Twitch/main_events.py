from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from main import Phaazebot

import asyncio
from Platforms.Twitch.api import getTwitchStreams
from Utils.Classes.twitchstream import TwitchStream

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
			self.BASE.Logger.debug("Running new twitch event check...", require="twitchevents:start")

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
				self.BASE.Logger.debug(f"No actions, delaying next check ({self.delay}s)", require="twitchevents:delay")
				return

			try:
				id_list:list = [ x["channel_id"] for x in res ]
				current_live_streams:list = await getTwitchStreams(self.BASE, id_list)

				if not current_live_streams:
					self.BASE.PhaazeDB.updateQuery( table="twitch_channel", content=dict(live=0), where="1=1" )
					self.BASE.Logger.debug(f"No channels live, delaying next check ({self.delay}s)", require="twitchevents:delay")
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

			await self.checkChanges(status_dict_db, status_dict_api)

			# update channels live in db
			await self.updateLive(current_live_streams)

			# update game in db
			await self.updateGame(current_live_streams)

	async def checkChanges(self, status_db:dict, status_api:dict) -> None:
		"""
			Checks the currently known channels stats in status_api,
			with the last known status in the status_db.

			Its easy to understand, a channel is gone offline
			if he is not in status_api but has live == True in the status_db
			and gone online when live == False but is found in the status_api
		"""

		event_offline:list = list()
		event_gamechange:list = list()
		event_live:list = list()

		for channel_id in status_db:

			EntryDB:StatusEntry = status_db[channel_id]
			EntryAPI:StatusEntry = status_api.get(channel_id, None)

			# API send nothing (means stream is not live)
			if not EntryAPI:

				# not found in api result, but was live in db
				# -> channel gone offline
				if EntryDB.live:
					event_offline.append(EntryDB)
					continue

				# not found in api result and was not live in db
				# -> do nothing... i guess
				else:
					continue

			# twitch gave us a result
			else:

				# we have a api result and it was not live in db
				# -> channel gone live
				if not EntryDB.live:
					event_live.append(EntryAPI)
					continue

				 # diffrent game id's
				 # -> game changed
				elif str(EntryAPI.game_id) != str(EntryDB.game_id):
					event_gamechange.append(EntryAPI)

		await self.eventOffline(event_offline)
		await self.eventGamechange(event_gamechange)
		await self.eventLive(event_live)

	# dict generator
	def generateStatusDB(self, db_result:list) -> dict:
		status_dict:dict = dict()

		for res in db_result:

			Entry:StatusEntry = StatusEntry()

			Entry.channel_id = str( res.get("channel_id", "") or "" )
			Entry.game_id = str( res.get("game_id", "") or "" )
			Entry.live = bool( res.get("live", 0) )

			status_dict[Entry.channel_id] = Entry

		return status_dict

	def generateStatusAPI(self, api_result:list) -> dict:
		status_dict:dict = dict()

		for TStream in api_result:

			Entry:StatusEntry = StatusEntry()

			Entry.channel_id = str( TStream.user_id or "" )
			Entry.game_id = str( TStream.game_id or "" )
			Entry.live = bool( TStream.stream_type == "live" )
			Entry.Stream = TStream

			status_dict[Entry.channel_id] = Entry

		return status_dict

	# updates
	async def updateLive(self, streams:list) -> None:
		channel_ids:str = ",".join(Chan.user_id for Chan in streams)
		self.BASE.PhaazeDB.query(f"""
			UPDATE `twitch_channel`
			SET `live` = CASE WHEN `twitch_channel`.`channel_id` IN ({channel_ids}) THEN 1 ELSE 0 END""",
		)
		self.BASE.Logger.debug("Updated DB - twitch_channel (live values)", require="twitchevents:game")

	async def updateGame(self, streams:list) -> None:
		game_sql:str = "UPDATE `twitch_channel` SET `game_id` = CASE"
		game_sql += "END WHERE 1=1"
		self.BASE.Logger.debug("Updated DB - twitch_game", require="twitchevents:game")

	# events
	async def eventLive(self, status_list:list) -> None:
		"""
			Event thats called for all twitch channels than gone live
			status_list is a list of StatusEntry()
			with the values from the twitch api
		"""
		if not status_list: return

		self.BASE.Logger.debug(f"Sending LIVE alerts for {len(status_list)} Twitch channels", require="twitchevents:live")

	async def eventGamechange(self, status_list:list) -> None:
		"""
			Event thats called for all twitch channels than gone offline
			status_list is a list of StatusEntry()
			with the values from the twitch api
		"""
		if not status_list: return

		self.BASE.Logger.debug(f"Sending GAMECHANGE alerts for {len(status_list)} Twitch channels", require="twitchevents:live")

	async def eventOffline(self, status_list:list) -> None:
		"""
			Event thats called for all twitch channels than gone offline
			status_list is a list of StatusEntry()
			with the last known values
		"""
		if not status_list: return

		self.BASE.Logger.debug(f"Sending OFFLINE alerts for {len(status_list)} Twitch channels", require="twitchevents:live")

class StatusEntry(object):
	"""
		Dummy class for API or DB Stream Status
	"""
	def __init__(self):
		self.channel_id:str = ""
		self.game_id:str = ""
		self.live:bool = False
		self.Stream:TwitchStream = None

	def __bool__(self):
		return bool(self.live)
