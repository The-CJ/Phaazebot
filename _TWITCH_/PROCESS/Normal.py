#BASE.modules._TWITCH_.PROCCESS.Normal

import asyncio, random

class Quote(object):

	custom_quote_cooldown = []

	async def Base(BASE, message, kwargs):
		#channel still in cooldown
		if message.channel_id in Quote.custom_quote_cooldown: return
		asyncio.ensure_future(Quote.cooldown(message.channel_id))

		channel_settings = kwargs.get('channel_settings', None)
		if channel_settings == None:
			channel_settings = await BASE.modules._Twitch_.Utils.get_channel_settings(BASE, message.channel_id)

		if channel_settings.get('active_quotes', False): return

		channel_quotes = kwargs.get('channel_quotes', None)
		if channel_quotes == None:
			channel_quotes = await BASE.modules._Twitch_.Utils.get_channel_quotes(BASE, message.channel_id)

		if len(channel_quotes) == 0:
			return await BASE.twitch.send_message(message.channel_name, 'This channel has no quotes.')

		index = None
		m = message.content.split(" ")
		if len(m) > 1:
			if m[1].isdigit():
				index = int(m[1])

		if index == None:
			index = random.choice([q.get('id', None) for q in channel_quotes])

		quote = None
		for quo in channel_quotes:
			if index == quo.get('id', None):
				quote = quo.get('content', '[N/A]')
				break

		if quote == None:
			return await BASE.twitch.send_message(message.channel_name, f"Quote '{str(index)}' was not found")

		return await BASE.twitch.send_message(message.channel_name, quote + f" [ID: {str(index)}]")

	async def cooldown(channel_id, cooldown=10):
		Quote.custom_quote_cooldown.append(channel_id)
		await asyncio.sleep(cooldown)
		Quote.custom_quote_cooldown.remove(channel_id)

