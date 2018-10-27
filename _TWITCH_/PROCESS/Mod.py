#BASE.modules._Twitch_.PROCESS.Mod

import asyncio

class Quote(object):

	async def add(BASE, message, kwargs):
		m = message.content[len(BASE.vars.TRIGGER_TWITCH):].split(" ")

		if len(m) <= 1:
			r = f"Error! > {BASE.vars.TRIGGER_TWITCH}addquote [Content]"
			return await BASE.twitch.send_message(message.channel_name, r)

		channel_quotes = await BASE.modules._Twitch_.Utils.get_channel_quotes(BASE, message.channel_id)

		if len(channel_quotes) >= BASE.limit.TWITCH_QUOTE_AMOUNT:
			return await BASE.twitch.send_message(message.channel_name, f"Error: There are already {BASE.limit.TWITCH_QUOTE_AMOUNT} quotes, delete some first")

		quote_content = " ".join(m[1:])

		ins = BASE.PhaazeDB.insert(into=f"twitch/quotes/quotes_{message.channel_id}", content=dict(content=quote_content))

		_id_ = ins.get('data', {}).get('id', '[N/A]')

		return await BASE.twitch.send_message(message.channel_name, f'Quote successfull added, ID: "{str(_id_)}"')

	async def rem(BASE, message, kwargs):
		m = message.content[len(BASE.vars.TRIGGER_TWITCH):].split(" ")

		if len(m) <= 1:
			r = f"Error! > {BASE.vars.TRIGGER_TWITCH}delquote [ID]"
			return await BASE.twitch.send_message(message.channel_name, r)

		_id_ = m[1] if m[1].isdigit() else None

		if _id_ == None:
			return await BASE.twitch.send_message(message.channel_name, f'"{str(_id_)}" is not a valid quote id')

		dele = BASE.PhaazeDB.delete(of=f"twitch/quotes/quotes_{message.channel_id}", where=f"str(data['id']) == str('{str(_id_)}')")
		h = dele.get('hits', 0)
		if h == 1:
			return await BASE.twitch.send_message(message.channel_name, f'Quote "{str(_id_)}" successfull deleted')
		else:
			return await BASE.twitch.send_message(message.channel_name, f' There is not quote with index "{str(_id_)}"')
