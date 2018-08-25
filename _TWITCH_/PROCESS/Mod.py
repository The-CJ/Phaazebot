#BASE.modules._Twitch_.PROCESS.Mod

import asyncio

class Quote(object):
	async def add(BASE, message, kwargs):
		m = message.content.split(" ")

		if len(m) <= 1:
			r = f"Error! > !addquote [Content]"
			return await BASE.twitch.send_message(message.channel_name, r)

		channel_quotes = await BASE.modules._Twitch_.Utils.get_channel_quotes(BASE, message.channel_id)

		if len(channel_quotes) >= 100:
			return await BASE.twitch.send_message(message.channel_name, "Error: There are allready 100 quotes, delete some first")

		quote_content = " ".join(m[1:])

		ins = BASE.PhaazeDB.insert(into=f"twitch/quotes/quotes_{message.channel_id}", content=dict(content=quote_content))

		_id_ = ins.get('data', {}).get('id', '[N/A]')

		return await BASE.twitch.send_message(message.channel_name, f'Quote successfull added, ID: "{str(_id_)}"')

	async def rem(BASE, message, kwargs):
		m = message.content.split(" ")

		if len(m) <= 2:
			r = f"Error! > !delquote [ID]"
			return await BASE.twitch.send_message(message.channel_name, r)

