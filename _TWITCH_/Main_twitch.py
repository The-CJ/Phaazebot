#BASE.modules.Twitch_IRC

import asyncio
import twitch_irc as twitch

#BASE.twitch
class Init_twitch(twitch.Client):
	def __init__(self, BASE):
		self.BASE = BASE
		super().__init__()
		self.lurker_loop_running = False

	async def on_ready(self):
		self.BASE.modules.Console.INFO("Twitch IRC Connected")

		#join own channel
		await self.join_channel(self.nickname)

		self.BASE.is_ready.twitch = True

		# Because Twitch like reconnecting us
		if not self.lurker_loop_running:
			self.lurker_loop_running = True
			asyncio.ensure_future( self.BASE.modules._Twitch_.Lurker.Base(self.BASE) )

		#join all channel
		await self.join_all()

	#message management
	async def on_message(self, message):
		if message.name.lower() == self.nickname.lower(): return
		if not self.BASE.is_ready.twitch: return

		await self.BASE.modules._Twitch_.Base.on_message(self.BASE, message)

	async def join_all(self):
		req = self.BASE.PhaazeDB.select(of="twitch/stream", where=f"data['chat_managed'] and data['twitch_name'] not in ['', None]", fields=["twitch_name"])
		data = req.get('data',[])
		self.BASE.modules.Console.DEBUG("Joining: " + ", ".join( channel.get('twitch_name', None) for channel in data ), require="twitch:join")

		#join limit / 30sec
		request_limit = 20

		for channel in data:
			channel_name = channel.get('twitch_name', None)
			if channel_name == None: continue
			await self.join_channel(channel_name)
			await asyncio.sleep(request_limit / 32)

		self.BASE.modules.Console.INFO(f'Joined all {str(len(data))} Twitch Channels')

	async def on_raw_data(self, r):
		pass
