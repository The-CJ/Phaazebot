#BASE.modules._Twitch_.Alerts

import asyncio, discord

#BASE.modules._Twitch_.Alerts.Main
class Init_Main(object):

	def __init__(self, BASE):
		super(Init_Main, self).__init__()
		self.running = True

		#add to BASE
		self.BASE = BASE
		BASE.modules._Twitch_.Alerts.Main = self

	def stop(self):
		self.running = False

	async def start(self):
		while self.running:
			all_alerts = self.BASE.PhaazeDB.select(of="twitch/alerts").get('data',[])
			try:
				live_streams = self.BASE.modules._Twitch_.Utils.get_streams( self.BASE, [s['twitch_id'] for s in all_alerts if s.get('twitch_id', None) != None])
				if live_streams.get('_total', 0) == 0:
					await asyncio.sleep(60*3)
					continue
				live_streams = live_streams.get('streams', 0)

			except:
				self.BASE.modules.Console.ERROR("No Twitch API Response")
				await asyncio.sleep(60*3)
				continue

			id_list_of_live_channel = [ str(stream.get('channel', {}).get('_id', 0)) for stream in live_streams ]
			old_ = self.generate_stream_obj(all_alerts, type_="db")
			new_ = self.generate_stream_obj(live_streams, type_="twitch")

			for twitch_id in old_:

				twitch_api_info = new_.get(twitch_id, {}).get('twitch_api_info', {})
				db_info = old_.get('db_info', {})

				old_status = old_[twitch_id].get('live', False)
				new_status = new_.get(twitch_id, {}).get('live', False)

				old_game = old_[twitch_id].get('game', None)
				new_game = new_.get(twitch_id, {}).get('game', None)

				# has gone live
				if old_status != new_status and new_status == True:
					self.event_live(twitch_info=twitch_api_info, db_info=db_info)

				# was live, changed game
				elif old_game != new_game and new_game != None:
					self.event_gamechange(twitch_info=twitch_api_info, db_info=db_info)


			sorted_games_id_list = self.sort_game_channel_list(live_streams)

			self.BASE.PhaazeDB.update(of="twitch/alerts", content=f"data['live'] = True if data['twitch_id'] in {str(id_list_of_live_channel)} else False")

			game_update = ""
			for game in sorted_games_id_list:
				id_list = sorted_games_id_list[game]
				game_update += f"data['game'] = '{game}' if data['twitch_id'] in {str(id_list)} else data.get('game', None);"

			self.BASE.PhaazeDB.update(of="twitch/alerts", content=game_update)
			await asyncio.sleep(20)

	def get_alert_info(self, twitch_id, prevent_new=False):
		check = self.BASE.PhaazeDB.select(of="twitch/alerts", where=f"data['twitch_id'] == '{twitch_id}'")
		if check.get('hits', 0) < 1:
			insert_ = dict()

			insert_['twitch_id'] = twitch_id
			insert_['live'] = False
			insert_['game'] = None
			insert_['discord_channel'] = []

			if not prevent_new: self.BASE.PhaazeDB.insert(into="twitch/alerts", content=insert_)
			return insert_

		return check.get('data',[])[0]

	def sort_game_channel_list(self, streams):
		r = {}

		for st in streams:

			game = st.get('game', "---")
			if r.get(game, None) == None:
				r[game] = []

			channel_id = st.get('channel', {}).get('_id', None)
			if channel_id != None:
				r[game].append( str(channel_id) )

		return r

	def generate_stream_obj(self, streams, type_="db"):
		r = {}

		for stream in streams:

			key = None
			game = None
			live = None

			twitch_api_info = None
			db_info = None

			if type_ == "db":
				key = stream.get('twitch_id', None)
				game = stream.get('game', None)
				live = stream.get('live', False)
				db_info = stream
			elif type_ == "twitch":
				key = stream.get('channel', {}).get('_id', None)
				game = stream.get('game', None)
				live = True
				twitch_api_info = stream

			r[str(key)] = dict( game=game, live=live, twitch_api_info=twitch_api_info, db_info=db_info )

		return r

	#Stream Events
	def event_live(self, twitch_info=dict(), db_info=dict()):
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
				chan = discord.Object(id=channel_id)
				asyncio.ensure_future(
					self.BASE.discord.send_message(chan, embed=emb),
					loop=self.BASE.Discord_loop
				)

	def event_gamechange(self, twitch_info=dict(), db_info=dict()):
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
			twitch_info = BASE.modules._Twitch_.Alerts.Main.get_alert_info(twitch_id)
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


