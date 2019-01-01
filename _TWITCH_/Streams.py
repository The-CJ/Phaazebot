#BASE.modules._Twitch_.Streams

import asyncio, discord, json

#BASE.modules._Twitch_.Streams.Main
class Init_Main(object):
	""" Provides a information source for other modules, so there don't have to make a api request to twitch"""

	def __init__(self, BASE):
		super(Init_Main, self).__init__()
		self.running = False
		self.live = []
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
				if not live_streams:
					await asyncio.sleep(self.refresh_time)
					continue

			except Exception as e:
				#nothing usual, just twitch things
				self.BASE.modules.Console.ERROR("No Twitch API Response\n"+str(e))
				await asyncio.sleep(self.refresh_time * 0.75)
				continue

			self.live = id_list_of_live_channel = [ str(stream.get('user_id', 0)) for stream in live_streams ]

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
					asyncio.ensure_future( self.event_live(twitch_info=twitch_info, db_info=db_info) )

				# was live, changed game
				elif old_game != new_game and new_game != None:
					asyncio.ensure_future( self.event_gamechange(twitch_info=twitch_info, db_info=db_info) )

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

			game = st.get('game_id', "---")
			if r.get(game, None) == None:
				r[game] = []

			channel_id = st.get('id', None)
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
				game = stream.get('game_id', None)
				live = stream.get('live', False)
				db_info = stream

			elif source == "twitch":
				key = stream.get('user_id', None)
				game = stream.get('game_id', None)
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
	def set_stream(self, twitch_id=None, create_new=False, **kwargs):
		if twitch_id == None: raise AttributeError("Missing 'twitch_id'")

		#check if allready exist
		if create_new:
			check = None
		else:
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
				self.BASE.modules.Console.INFO(f"New Sream Entry created: {twitch_id}")
				self.BASE.PhaazeDB.insert( into="twitch/stream", content=insert )
				return insert
			except:
				return False

		#update existing
		update = dict()
		for key in kwargs:
			check[key] = kwargs[key]
			update[key] = kwargs[key]
		update['twitch_id'] = twitch_id

		try:
			self.BASE.PhaazeDB.update( of="twitch/stream", where=f"data['twitch_id'] == {json.dumps(twitch_id)}", content=update )
			return check
		except:
			return False

	def get_stream(self, twitch_id, create_new=False, **kwargs):
		check = self.BASE.PhaazeDB.select(of="twitch/stream", where=f"data['twitch_id'] == {json.dumps(twitch_id)}", limit=1)
		if check.get('hits', 0) < 1:
			#create new
			if create_new:
				return self.set_stream(twitch_id=twitch_id, create_new=True, **kwargs)
			else:
				return None
		return check.get('data',[])[0]

	#Stream Events
	async def event_live(self, twitch_info=dict(), db_info=dict()):
		if not self.BASE.active.twitch_alert: return

		if twitch_info.get('type', None) != 'live': return

		game = twitch_info.get('game_id', '[N/A]')
		logo = twitch_info.get('thumbnail_url', None)
		display_name = twitch_info.get('user_name', '[N/A]')
		url = "https://www.twitch.tv/"+twitch_info.get('user_name', "[N/A]")
		status = twitch_info.get('title', '[N/A]')

		#Discord
		discord_channel = db_info.get('alert_discord_channel', [])
		if discord_channel:

			raw_custom_formats = self.BASE.PhaazeDB.select( of="twitch/alert_format",where=f"data['discord_channel_id'] in str({json.dumps(discord_channel)})" ).get("data", [])

			channel_format_index = dict()
			for raw_alert_format in raw_custom_formats:
				channel_format_index[raw_alert_format.get('discord_channel_id', '-')] = raw_alert_format.get("custom_alert", None)

			emb = discord.Embed(title=status, url=url, description=f":game_die: Playing: **{game}**", color=0x6441A4)
			emb.set_author(name=display_name, url=url, icon_url=logo)
			emb.set_footer(text="Provided by Twitch.tv", icon_url=self.BASE.vars.twitch_logo)
			emb.set_image(url=logo)

			for channel_id in discord_channel:
				#check for custom format
				alert_format = channel_format_index.get(channel_id, None)

				chan = discord.Object(id=channel_id)
				asyncio.ensure_future(
					self.BASE.discord.send_message(chan, content=alert_format, embed=emb),
					loop=self.BASE.Discord_loop
				)

	async def event_gamechange(self, twitch_info=dict(), db_info=dict()):
		if not self.BASE.active.twitch_alert: return

		if twitch_info.get('type', None) != 'live': return

		game = twitch_info.get('game_id', '[N/A]')
		logo = twitch_info.get('thumbnail_url', None)
		display_name = twitch_info.get('user_name', '[N/A]')
		url = "https://www.twitch.tv/"+twitch_info.get('user_name', "[N/A]")
		status = twitch_info.get('title', '[N/A]')

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
		def toggle_chan(BASE, twitch_id, discord_channel_id, **kwargs):
			twitch_info = BASE.modules._Twitch_.Streams.Main.get_stream(twitch_id, create_new=True, **kwargs)
			twitch_discord_channel_list = twitch_info.get('alert_discord_channel', [])

			if discord_channel_id in twitch_discord_channel_list:
				twitch_discord_channel_list.remove(discord_channel_id)
				state = 'remove'
			else:
				twitch_discord_channel_list.append(discord_channel_id)
				state = 'add'

			BASE.PhaazeDB.update(
				of="twitch/stream",
				where=f"str(data['twitch_id']) == str({json.dumps(twitch_id)})",
				content=dict(alert_discord_channel=twitch_discord_channel_list))

			return state

		def get_alerts_for_channel(BASE, channel_id):
			res = BASE.PhaazeDB.select(	of=f"twitch/stream",  where=f"'{channel_id}' in data['alert_discord_channel']" ).get("data", [])
			return res

		def clear_channel_alerts(BASE, channel_id):
			compare = BASE.modules._Twitch_.Streams.Main.Discord.get_alerts_for_channel(BASE, channel_id)

			r = []

			for chan in compare:
				twitch_id = chan.get('twitch_id', None)
				if twitch_id == None: continue
				r.append( dict(twitch_id=twitch_id, twitch_name=chan.get('twitch_name', '[N/A]')) )
				chan['alert_discord_channel'].remove(channel_id)

				BASE.PhaazeDB.update(
					of = f"twitch/stream",
					limit=1,
					where = f"data['twitch_id'] == '{twitch_id}'",
					content = dict (alert_discord_channel = chan['alert_discord_channel'])
				)
			return r

