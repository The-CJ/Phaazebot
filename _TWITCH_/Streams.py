#BASE.modules._Twitch_.Streams

import asyncio, discord, json

#BASE.modules._Twitch_.Streams.Main
class Init_Main(object):
	""" Provides a information source for other modules, so there don't have to make a api request to twitch"""

	def __init__(self, BASE):
		super(Init_Main, self).__init__()
		self.running = False
		self.refresh_time = 50

		#add to BASE
		self.BASE = BASE

	def stop(self):
		if not self.running: raise Exception("not running")
		self.running = False

	async def start(self):
		if self.running: raise Exception("allready running")

		self.running = True
		while self.running and self.BASE.active.twitch_stream:

			# to reduce twitch requests as much as possible, we only update channels,
			# that have at least one discord channel to alert or have Phaaze in the twitch channel

			need_to_check = self.BASE.PhaazeDB.select(of="twitch/stream", where="data['chat_managed'] or data['alert_discord_channel']").get("data", [])

			try:
				live_streams = self.BASE.modules._Twitch_.Utils.get_streams( self.BASE, [s['twitch_id'] for s in need_to_check if s.get('twitch_id', None) != None])
				# no channel are live -> no updates
				if live_streams.get('_total', 0) == 0:
					await asyncio.sleep(self.refresh_time)
					continue

			except Exception as e:
				#nothing usual, just twitch things
				self.BASE.modules.Console.ERROR("No Twitch API Response\n"+str(e))
				await asyncio.sleep(self.refresh_time * 0.75)
				continue

			live_streams = live_streams.get("streams",[])
			id_list_of_live_channel = [ str(stream.get('channel', {}).get('_id', 0)) for stream in live_streams ]

			old_list = self.generate_stream_list(need_to_check, source="db")
			new_list = self.generate_stream_list(live_streams, source="twitch")

			# every entry in new_list has a entry in old_list
			# but not vise versa
			# because the opposite in new_list is only there, if the channel is live

			for entry in old_list:

				old_stream = old_list.get(entry, {})
				new_stream = new_list.get(entry, {}) # <- only there if live

				twitch_info = new_stream.get('twitch_api_info', {})
				db_info = old_stream.get('db_info', {})

				old_status = old_stream.get('live', False)
				new_status = new_stream.get('live', False)

				old_game = old_stream.get('game', None)
				new_game = new_stream.get('game', None)

				# has gone live
				if old_status != new_status and new_status == True:

					self.event_live(twitch_info=twitch_info, db_info=db_info)

				# was live, changed game
				elif old_game != new_game and new_game != None:
					self.event_gamechange(twitch_info=twitch_info, db_info=db_info)

			sorted_list_of_streams_per_game = self.sort_channel_per_game(live_streams)

			update_string = f"data['live'] = True if data['twitch_id'] in {str(id_list_of_live_channel)} else False;"

			for game in sorted_list_of_streams_per_game:
				id_channel_list = sorted_list_of_streams_per_game[game]
				update_string += f"data['game'] = {json.dumps(game)} if data['twitch_id'] in {str(id_channel_list)} else data.get('game', None);"

			self.BASE.PhaazeDB.update(of="twitch/stream", content=update_string)
			await asyncio.sleep(self.refresh_time)

	# utils
	def sort_channel_per_game(self, streams):
		r = {}

		for st in streams:

			game = st.get('game', "---")
			if r.get(game, None) == None:
				r[game] = []

			channel_id = st.get('channel', {}).get('_id', None)
			if channel_id != None:
				r[game].append( str(channel_id) )

		return r

	def generate_stream_list(self, streams, source="db"):
		r = dict()

		for stream in streams:

			key = None
			game = None
			live = None

			twitch_api_info = None
			db_info = None

			if source == "db":
				key = stream.get('twitch_id', None)
				game = stream.get('game', None)
				live = stream.get('live', False)
				db_info = stream

			elif source == "twitch":
				key = stream.get('channel', {}).get('_id', None)
				game = stream.get('game', None)
				live = True
				twitch_api_info = stream

			r[str(key)] = dict(
				game=game,
				live=live,
				twitch_api_info=twitch_api_info,
				db_info=db_info
			)

		return r

	#functions
	def set_stream(self, twitch_id=None, **kwargs):
		if twitch_id == None: raise AttributeError("Missing 'twitch_id'")

		#check if allready exist
		check = self.get_stream(twitch_id)

		#new entry
		if check == None:
			insert = dict(
				alert_discord_channel = kwargs.get("alert_discord_channel", []),
				chat_managed = kwargs.get("chat_managed", False),
				game = kwargs.get("game", None),
				live = kwargs.get("live", False),
				twitch_id = twitch_id,
				twitch_name = kwargs.get("twitch_name", None)
			)
			try:
				self.BASE.PhaazeDB.select( into="twitch/stream", content=insert )
				return True
			except:
				return False

		#update existing
		update = dict()
		for key in kwargs:
			update[key] = kwargs[key]
		update['twitch_id'] = twitch_id

		try:
			self.BASE.PhaazeDB.update( of="twitch/stream", where=f"data['twitch_id'] == {json.dumps(twitch_id)}", content=update )
			return True
		except:
			return False

	def get_stream(self, twitch_id):
		check = self.BASE.PhaazeDB.select(of="twitch/stream", where=f"data['twitch_id'] == {json.dumps(twitch_id)}")
		if check.get('hits', 0) < 1:
			return None
		return check.get('data',[])[0]

	#Stream Events
	def event_live(self, twitch_info=dict(), db_info=dict()):
		if not self.BASE.active.twitch_alert: return

		if twitch_info.get('stream_type', None) != 'live': return

		game = twitch_info.get('game', '[N/A]')
		logo = twitch_info.get('channel', {}).get('logo', '[N/A]')
		display_name = twitch_info.get('channel', {}).get('display_name', '[N/A]')
		url = twitch_info.get('channel', {}).get('url', '[N/A]')
		status = twitch_info.get('channel', {}).get('status', '[N/A]')

		#Discord
		discord_channel = db_info.get('discord_channel', [])
		if discord_channel:
			emb = discord.Embed(title=status, url=url, description=f":game_die: Playing: **{game}**", color=0x6441A4)
			emb.set_author(name=display_name, url=url, icon_url=logo)
			emb.set_footer(text="Provided by Twitch.tv", icon_url=self.BASE.vars.twitch_logo)
			emb.set_image(url=logo)

			for channel_id in discord_channel:
				#check for custom format
				alert_format = None
				res = self.BASE.PhaazeDB.select(of="twitch/alert_format", where=f"data['discord_channel_id'] == '{channel_id}'", limit=1)
				if res.get('data', []):
					alert_format = res.get('data', [])[0].get('custom_alert', None)

				chan = discord.Object(id=channel_id)
				asyncio.ensure_future(
					self.BASE.discord.send_message(chan, content=alert_format, embed=emb),
					loop=self.BASE.Discord_loop
				)

	def event_gamechange(self, twitch_info=dict(), db_info=dict()):
		if not self.BASE.active.twitch_alert: return

		if twitch_info.get('stream_type', None) != 'live': return

		game = twitch_info.get('game', '[N/A]')
		logo = twitch_info.get('channel', {}).get('logo', '[N/A]')
		display_name = twitch_info.get('channel', {}).get('display_name', '[N/A]')
		url = twitch_info.get('channel', {}).get('url', '[N/A]')
		status = twitch_info.get('channel', {}).get('status', '[N/A]')

		#Discord
		discord_channel = db_info.get('discord_channel', [])
		if discord_channel:
			emb = discord.Embed(title=status, url=url, description=f":game_die: Now Playing: **{game}**", color=0x6441A4)
			emb.set_author(name=display_name, url=url, icon_url=logo)
			emb.set_footer(text="Provided by Twitch.tv", icon_url=self.BASE.vars.twitch_logo)
			emb.set_thumbnail(url=logo)

			for channel_id in discord_channel:
				chan = discord.Object(id=channel_id)
				asyncio.ensure_future(
					self.BASE.discord.send_message(chan, embed=emb),
					loop=self.BASE.Discord_loop
				)

	class Discord(object):
		def toggle_chan(BASE, twitch_id, discord_channel_id):
			twitch_info = BASE.modules._Twitch_.Alerts.Main.get_stream(twitch_id)
			twitch_discord_channel_list = twitch_info.get('discord_channel', [])

			if discord_channel_id in twitch_discord_channel_list:
				twitch_discord_channel_list.remove(discord_channel_id)
				state = 'remove'
			else:
				twitch_discord_channel_list.append(discord_channel_id)
				state = 'add'

			BASE.PhaazeDB.update(
				of="twitch/alerts",
				where=f"data['twitch_id'] == '{twitch_id}'",
				content=dict(discord_channel=twitch_discord_channel_list))

			return state


