from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from main import Phaazebot

import asyncio
from Utils.Classes.twitchstream import TwitchStream
from Utils.Classes.twitchgame import TwitchGame
from Utils.Classes.twitchuser import TwitchUser
from Platforms.Twitch.api import getTwitchStreams, getTwitchGames, getTwitchUsers
from Platforms.Discord.twitchalerts import discordHandleLive, discordHandleOffline, discordHandleGameChange

class PhaazebotTwitchEvents(object):
	"""
		This Module is to keep track of all events related to twitch
		and is the part that keeps phaaze db updates
		so we can reduce twitch api calls as much as possible.
		Under events fall:
			- a channel going live
			- a channel changes his game
			- a channel goes offline
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
				`twitch_channel`.`live`
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
		await self.updateChannelLive(current_live_streams)

		# update game in db
		await self.updateChannelGame(current_live_streams)

	async def checkChanges(self, status_db:dict, status_api:dict) -> None:
		"""
			Checks the currently known channels stats in status_api,
			with the last known status in the status_db.

			Its easy to understand, a channel is gone offline
			if he is not in status_api but has live == True in the status_db
			and gone online when live == False but is found in the status_api
		"""

		detected_events:list = list()

		for channel_id in status_db:

			EntryDB:StatusEntry = status_db[channel_id]
			EntryAPI:StatusEntry = status_api.get(channel_id, None)

			# API send nothing (means stream is not live)
			if not EntryAPI:

				# not found in api result, but was live in db
				# -> channel gone offline
				if EntryDB.live:
					detected_events.append( [0, EntryDB] )
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
					detected_events.append( [1, EntryAPI] )
					continue

				 # diffrent game id's
				 # -> game changed
				elif str(EntryAPI.game_id) != str(EntryDB.game_id):
					detected_events.append( [2, EntryAPI] )
					continue

		return await self.handleEvents(detected_events)

	async def handleEvents(self, events:list) -> None:
		"""
			Complets all events, which means, get game data, user data, etc...
			and then call the individual events.
			All entrys in 'events' are small lists, containing a int in pos 0
			and a StatusEntry in pos 1

			Pos 0 can be:
				0 = offline event
				1 = going live event
				2 = game change event
		"""
		if not events: return

		self.BASE.Logger.debug(f"Processing {len(events)} Twitch Events", require="twitchevents:processing")

		# the following 2 dicts are key based with a simple None value
		# every key must be searched in the twitch api for infos
		# (actully just needed for games, because users are unique)
		needed_games:dict = dict()
		needed_users:dict = dict()

		for event in events:
			Status:StatusEntry = event[1]
			needed_games[str(Status.game_id)] = None
			needed_users[str(Status.channel_id)] = None

		needed_games = await self.fillGameData(needed_games)
		needed_users = await self.fillUserData(needed_users)

		alert_list_live:list = list()
		alert_list_gamechange:list = list()
		alert_list_offline:list = list()

		for event in events:
			Status:StatusEntry = event[1]
			Status.Game = needed_games.get(Status.game_id, None)
			Status.User = needed_users.get(Status.channel_id, None)

			if event[0] == 0:
				alert_list_offline.append(Status)

			elif event[0] == 1:
				alert_list_live.append(Status)

			elif event[0] == 2:
				alert_list_gamechange.append(Status)

			else:
				self.BASE.Logger.warning(f"Unknown Status Event number: {event[0]}")

		# update db
		asyncio.ensure_future( self.updateTwitchGames(needed_games) )
		asyncio.ensure_future( self.updateTwitchUserNames(needed_users) )

		# launch events
		asyncio.ensure_future( self.eventLive(alert_list_live) )
		asyncio.ensure_future( self.eventOffline(alert_list_offline) )
		asyncio.ensure_future( self.eventGamechange(alert_list_gamechange) )

	# dict generator
	def generateStatusDB(self, db_result:list) -> dict:
		"""
			Generates a StatusEntry
			filled with standard infos from DB
			Later, this object may get added with a Game and/or a Channel object
		"""
		status_dict:dict = dict()

		for res in db_result:

			Entry:StatusEntry = StatusEntry()

			Entry.channel_id = str( res.get("channel_id", "") or "" )
			Entry.game_id = str( res.get("game_id", "") or "" )
			Entry.live = bool( res.get("live", 0) )

			status_dict[Entry.channel_id] = Entry

		return status_dict

	def generateStatusAPI(self, api_result:list) -> dict:
		"""
			Generates a StatusEntry
			filled with all infos from API
			also adds the TwitchStream object as self.Stream
			Later, this object may get added with a Game and/or a Channel object
		"""
		status_dict:dict = dict()

		for TStream in api_result:

			Entry:StatusEntry = StatusEntry()

			Entry.channel_id = str( TStream.user_id or "" )
			Entry.game_id = str( TStream.game_id or "" )
			Entry.live = bool( TStream.stream_type == "live" )
			Entry.Stream = TStream

			status_dict[Entry.channel_id] = Entry

		return status_dict

	# api gatherer
	async def fillGameData(self, requested_games:dict) -> dict:
		"""
			Tryes to get requested games by existing dict keys
			value of these keys does not matter
		"""

		id_list:list = [ g for g in requested_games ]
		result_game:list = await getTwitchGames(self.BASE, id_list)

		Game:TwitchGame
		for Game in result_game:
			requested_games[str(Game.game_id)] = Game

		return requested_games

	async def fillUserData(self, requested_users:dict) -> dict:
		"""
			Tryes to get requested user by existing dict keys
			value of these keys does not matter
		"""

		id_list:list = [ u for u in requested_users ]
		result_user:list = await getTwitchUsers(self.BASE, id_list)

		User:TwitchUser
		for User in result_user:
			requested_users[str(User.user_id)] = User

		return requested_users

	# updates
	async def updateChannelLive(self, streams:list) -> None:
		"""
			Updates the `live` col in DB, according to all entrys in `streams`
			`streams` is a list of TwitchStream
		"""
		Stream:TwitchStream
		channel_ids:str = ','.join( f"'{Stream.user_id}'" for Stream in streams )
		if not channel_ids: channel_ids = "0"

		self.BASE.PhaazeDB.query(f"""
			UPDATE `twitch_channel`
			SET `live` = CASE WHEN `twitch_channel`.`channel_id` IN ({channel_ids}) THEN 1 ELSE 0 END""",
		)
		self.BASE.Logger.debug("Updated DB - twitch_channel (live)", require="twitchevents:db")

	async def updateChannelGame(self, streams:list) -> None:
		"""
			Updates the `game_id` col in DB, according to all entrys in `streams`
			`streams` is a list of TwitchStream
		"""
		# create a dict with `game_id` as keys
		# and a list of channel_ids as that are playing this game as value
		game_dict:dict = dict()

		Stream:TwitchStream
		for Stream in streams:
			if game_dict.get(Stream.game_id, None) == None:
				game_dict[Stream.game_id] = list()
			game_dict[Stream.game_id].append(Stream.user_id)

		# build update sql
		game_sql:str = "UPDATE `twitch_channel` SET `game_id` = CASE"

		for game_id in game_dict:
			playing:str = ','.join( f"'{chan_id}'" for chan_id in game_dict[game_id] )
			if not playing: playing = "0" # should never happen
			game_sql += f" WHEN `twitch_channel`.`channel_id` IN ({playing}) THEN '{game_id}'"

		game_sql += " ELSE `game_id` END WHERE 1=1"

		self.BASE.PhaazeDB.query(game_sql)
		self.BASE.Logger.debug("Updated DB - twitch_channel (game_id)", require="twitchevents:db")

	async def updateTwitchGames(self, update_games:dict) -> None:
		"""
			updates the twitch_game db with data we gathered before
		"""

		sql:str = "REPLACE INTO `twitch_game` (`game_id`,`name`) VALUES "
		sql_additions:list = list()
		sql_values:tuple = tuple()

		for game_id in update_games:
			Game:TwitchGame = update_games[game_id]
			if not Game: continue # could be unfound in api from .fillGameData and still be False

			sql_additions.append( "(%s, %s)" )	
			sql_values += (Game.game_id, Game.name)

		# no requested games are found in API, SQL whould be invalid -> skip
		if (not sql_values) or (not sql_additions): return
		sql += ','.join(sql_additions)

		self.BASE.PhaazeDB.query(sql, sql_values)
		self.BASE.Logger.debug(f"Updated DB - twitch_game {len(update_games)} Entry(s)", require="twitchevents:db")

	async def updateTwitchUserNames(self, update_users:dict) -> None:
		"""
			updates the twitch_user_name db with data we gathered before
		"""

		sql:str = "REPLACE INTO `twitch_user_name` (`user_id`, `user_name`, `user_display_name`) VALUES "
		sql_additions:list = list()
		sql_values:tuple = tuple()

		for user_id in update_users:
			User:TwitchUser = update_users[user_id]
			if not User: continue # could be unfound in api from .fillUserData and still be False

			sql_additions.append( "(%s, %s, %s)" )
			sql_values += (User.user_id, User.name, User.display_name)

		# no requested users are found in API, SQL whould be invalid -> skip
		if (not sql_values) or (not sql_additions): return
		sql += ','.join(sql_additions)

		self.BASE.PhaazeDB.query(sql, sql_values)
		self.BASE.Logger.debug(f"Updated DB - twitch_user_name {len(update_users)} Entrys(s)", require="twitchevents:db")

	# events
	async def eventLive(self, status_list:list) -> None:
		"""
			Event thats called for all twitch channels than gone live
			status_list is a list of StatusEntry()
			with the values from the twitch api
		"""
		if not status_list: return

		self.BASE.Logger.debug(f"Received LIVE alerts for {len(status_list)} Twitch channels", require="twitchevents:live")

		if self.BASE.Discord:
			# give infos to discord loop and give out alerts
			asyncio.ensure_future( discordHandleLive(self.BASE.Discord, status_list), loop=self.BASE.DiscordLoop )
		else:
			self.BASE.Logger.debug(f"Skipping Twitch Alerts for Discord, it is not active", require="twitchevents:live")

	async def eventGamechange(self, status_list:list) -> None:
		"""
			Event thats called for all twitch channels than are still live but changed there game
			status_list is a list of StatusEntry()
			with the values from the twitch api
		"""
		if not status_list: return

		self.BASE.Logger.debug(f"Received GAMECHANGE alerts for {len(status_list)} Twitch channels", require="twitchevents:live")

		if self.BASE.Discord:
			# give infos to discord loop and give out alerts
			asyncio.ensure_future( discordHandleGameChange(self.BASE.Discord, status_list), loop=self.BASE.DiscordLoop )
		else:
			self.BASE.Logger.debug(f"Skipping Twitch Alerts for Discord, it is not active", require="twitchevents:live")

	async def eventOffline(self, status_list:list) -> None:
		"""
			Event thats called for all twitch channels than gone offline
			status_list is a list of StatusEntry()
			with the last known values from phaaze db
		"""
		if not status_list: return

		self.BASE.Logger.debug(f"Received OFFLINE alerts for {len(status_list)} Twitch channels", require="twitchevents:live")

		if self.BASE.Discord:
			# give infos to discord loop and give out alerts
			asyncio.ensure_future( discordHandleOffline(self.BASE.Discord, status_list), loop=self.BASE.DiscordLoop )
		else:
			self.BASE.Logger.debug(f"Skipping Twitch Alerts for Discord, it is not active", require="twitchevents:live")

class StatusEntry(object):
	"""
		Dummy class for API or DB Stream Status
	"""
	def __init__(self):
		self.channel_id:str = ""
		self.game_id:str = ""
		self.live:bool = False

		self.Stream:TwitchStream = None
		self.User:TwitchUser = None
		self.Game:TwitchGame = None

	def __repr__(self):
		return f"<{self.__class__.__name__} Stream={self.Stream} Game={self.Game} User={self.User} >"

	def __bool__(self):
		return bool(self.live)
