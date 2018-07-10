#BASE.modules._TWITCH_.PROCCESS.Normal

import asyncio

class Quote(object):
	async def Base(BASE, message, kwargs):
		channel_settings = kwargs.get('channel_settings', None)
		if channel_settings == None:
			channel_settings = await BASE.modules._Twitch_.Utils.get_channel_settings(BASE, message.channel_id)

		if channel_settings.get('active_quotes', False): return

		channel_quotes = await BASE.modules._Twitch_.Utils.get_channel_quotes(BASE, message.channel_id)
		print(channel_quotes) # TODO: make quotes quoting again