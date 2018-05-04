#BASE.modules._TWITCH_.CMD.Normal

import asyncio, json, random


block_q = []
async def block_quotes(_id_):
	block_q.append(_id_)
	await asyncio.sleep(5)
	block_q.remove(_id_)

async def Quote(BASE, message):
	if message.room_id in block_q: return
	asyncio.ensure_future(block_quotes(message.room_id))
	file = await BASE.modules._Twitch_.Utils.get_twitch_file(BASE, message.room_id)
	allow_quotes = file.get("quote_active", False)
	if not allow_quotes: return

	all_quotes = file.get("quotes", [])
	if len(all_quotes) == 0:
		return await BASE.Twitch_IRC_connection.send_message(message.channel, "This channel doesn't have quotes!")

	m = message.content.split(" ")

	if len(m) == 1:
		q = random.choice(all_quotes)
		return await BASE.Twitch_IRC_connection.send_message(
				message.channel,
				"{0} - #{1}".format(q["content"], str(q["index"])))

	elif len(m) > 1:
		if not m[1].isdigit():
			return

		for q in all_quotes:
			if q["index"] == int(m[1]):
				return await BASE.Twitch_IRC_connection.send_message(
						message.channel,
						"{0} - #{1}".format(q["content"], str(q["index"])))

		return await BASE.Twitch_IRC_connection.send_message(
				message.channel,
				"@{0}, There is no Quote {1}".format(message.save_name, m[1]))
