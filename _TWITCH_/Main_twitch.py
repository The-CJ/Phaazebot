#BASE.modules.Twitch_IRC

import asyncio, traceback
import twitch_irc as twitch

#BASE.twitch
class Init_twitch(twitch.Client):
	def __init__(self, BASE):
		self.BASE = BASE
		super().__init__()
		self.live = [] # string list of channel id's

	async def on_ready(self):
		self.BASE.modules.Console.GREEN("SUCCESS", "Twitch IRC Connected")

		#join all channel
		await self.join_channel(self.nickname)

		await self.join_all()
		self.BASE.is_ready.twitch = True

	#message management
	async def on_message(self, message):
		if message.name.lower() == self.nickname.lower(): return
		if not self.BASE.is_ready.twitch: return

		await self.BASE.modules._Twitch_.Base.on_message(self.BASE, message)

	async def join_all(self):
		req = self.BASE.PhaazeDB.select(of="setting/twitch_channel")
		data = req.get('data',[])

		#join limit / 30sec
		request_limit = 20

		for channel in data:
			channel_name = channel.get('twitch_name', None)
			if channel_name == None: continue
			await self.join_channel(channel_name)
			await asyncio.sleep(request_limit / 32)

		self.BASE.modules.Console.GREEN('SUCCESS', f'Joined all {str(len(data))} Channels')