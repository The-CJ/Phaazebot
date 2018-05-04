#BASE.modules._TWITCH_.CMD.Mods

import asyncio, random, json, time
max_quotes = 200
already_in_pairing_proccess = []

class Quotes(object):
	async def add(BASE,message):
		if not (message.channel == message.name or message.mod): return
		m = message.content.split(" ")
		if len(m) == 1:
			return await BASE.Twitch_IRC_connection.send_message(
					message.channel,
					"@{0}, Missing arguments | !addquote [quote]".format(message.save_name))

		else:
			file = await BASE.modules._Twitch_.Utils.get_twitch_file(BASE, message.room_id)
			all_quotes = file["quotes"] = file.get("quotes", [])
			check = [q["index"] for q in all_quotes]
			if len(check) > 198:
				await BASE.Twitch_IRC_connection.send_message(
					message.channel,
					"Quote not added, the channel reached the maximum of {0} quotes".format(max_quotes))

			q_content = " ".join(word for word in m[1:])
			q_index = await Quotes.get_index(check)

			new_quote = {"index": q_index, "content": q_content}
			file["quotes"].append(new_quote)

			with open("_TWITCH_/Channel_files/{0}.json".format(message.room_id), "w") as new:
				json.dump(file, new)
				setattr(BASE.twitchfiles, "channel_"+message.room_id, file)
				await BASE.Twitch_IRC_connection.send_message(
					message.channel,
					"Quote added: {0} - {1}".format(q_content, str(q_index)))

	async def rem(BASE,message):
		if not (message.channel == message.name or message.mod): return
		m = message.content.split(" ")
		if len(m) == 1:
			return await BASE.Twitch_IRC_connection.send_message(
				message.channel,
				"@{0}, Missing arguments | !delquote [index]".format(message.save_name))

		file = await BASE.modules._Twitch_.Utils.get_twitch_file(BASE, message.room_id)

		if not m[1].isdigit():
			return await BASE.Twitch_IRC_connection.send_message(
				message.channel,
				"@{0}, Invalid arguments".format(message.save_name))

		all_quotes = file["quotes"] = file.get("quotes", [])
		for q in all_quotes:
			if q["index"] == int(m[1]):
				file["quotes"].remove(q)
				with open("_TWITCH_/Channel_files/{0}.json".format(message.room_id), "w") as new:
					json.dump(file, new)
					setattr(BASE.twitchfiles, "channel_"+message.room_id, file)
					return await BASE.Twitch_IRC_connection.send_message(
						message.channel,
						"Quote {0} removed!".format(str(q["index"])))
		return await BASE.Twitch_IRC_connection.send_message(
			message.channel,
			"Quote {0} not found!".format(str(m[1])))

	async def get_index(check):
		to_compare = list(range(1, max_quotes+1))
		for obj in check:
			to_compare.remove(obj)

		return random.choice(to_compare)

class Coms(object):
	async def add(BASE,message):
		if not (message.channel == message.name or message.mod): return
		m = message.content.split(" ")
		if len(m) <= 2:
			return await BASE.Twitch_IRC_connection.send_message(
					message.channel,
					"@{0}, Missing arguments | !addcom [trigger] [content]".format(message.save_name))

		else:
			file = await BASE.modules._Twitch_.Utils.get_twitch_file(BASE, message.room_id)
			all_coms = file["commands"] = file.get("commands", [])
			check = [c["trigger"] for c in all_coms]

			if m[1].lower() in check:
				#replace
				for command in all_coms:
					if m[1].lower() == command["trigger"]:
						command["content"] = " ".join(w for w in m[2:])
						resp = "Command: '{0}' successful updated."

			else:
				#new
				new_com = {"trigger": m[1].lower(), "content": " ".join(w for w in m[2:]) }
				file["commands"].append(new_com)
				resp = "Command: '{0}' successful created."

			with open("_TWITCH_/Channel_files/{0}.json".format(message.room_id), "w") as new:
				json.dump(file, new)
				setattr(BASE.twitchfiles, "channel_"+message.room_id, file)
				await BASE.Twitch_IRC_connection.send_message(
					message.channel,
					resp.format(m[1]))

	async def rem(BASE,message):
		if not (message.channel == message.name or message.mod): return
		m = message.content.split(" ")
		if len(m) == 1:
			return await BASE.Twitch_IRC_connection.send_message(
				message.channel,
				"@{0}, Missing arguments | !delcom [trigger]".format(message.save_name))

		file = await BASE.modules._Twitch_.Utils.get_twitch_file(BASE, message.room_id)

		all_coms = file["commands"] = file.get("commands", [])
		for c in all_coms:
			if c["trigger"] == m[1].lower():
				file["commands"].remove(c)
				with open("_TWITCH_/Channel_files/{0}.json".format(message.room_id), "w") as new:
					json.dump(file, new)
					setattr(BASE.twitchfiles, "channel_"+message.room_id, file)
					return await BASE.Twitch_IRC_connection.send_message(
						message.channel,
						"Command '{0}' removed!".format(c["trigger"]))

		return await BASE.Twitch_IRC_connection.send_message(
			message.channel,
			"@{0}, Command: '{1}' not found.".format(message.save_name, m[1]))

async def verify(BASE, message):
	if not message.channel == message.name: return

	m = message.content.split(" ")

	if len(m) == 1:
		confirm = await BASE.modules._Twitch_.Utils.get_opposite_osu_twitch(BASE, message.room_id, platform="twitch")
		if confirm == None:
			if message.room_id in already_in_pairing_proccess:
				return await BASE.Twitch_IRC_connection.send_message(message.name, "@{0} You are already in a verify proccess. if you forgot your Number wait 5min and try it again.".format(message.save_name))
			pair_number = str(BASE.modules._Osu_.Utils.pairing_object(BASE, twitch_id=str(message.room_id), twitch_name=message.save_name).verify)
			await BASE.Twitch_IRC_connection.send_message(message.name, "@{1} Your account is not paired to a Osu! account. | Send {2} a privat osu! ingame message with '!verify {0}' to pair it. (you have 5min)".format(pair_number, message.save_name, BASE.Osu_IRC.nickname))
			already_in_pairing_proccess.append(message.room_id)

		else:
			await BASE.Twitch_IRC_connection.send_message(message.name, "Your account is paired! Twitch channel: {0} | Osu Account: {1}".format(confirm["twitch"]["name"], confirm["osu"]["name"]))
			await BASE.Twitch_IRC_connection.send_message(message.name, "Wanna break your connection? --> '!disconnect'")

	elif len(m) == 2:
		a_o = None
		for aouth_o in BASE.queue.twitch_osu_verify:
			if str(aouth_o.verify) == m[1]:
				a_o = aouth_o

		if a_o == None:
			await BASE.Twitch_IRC_connection.send_message(message.name, "{0} is not awaited for verify, be sure to don't make typos. (like i do all the time LUL)".format(m[1]))

		else:
			aouth_o.twitch_id = message.room_id
			aouth_o.twitch_name = message.name
			await BASE.Twitch_IRC_connection.send_message(message.name, "Your Twitch name has been set. If everything is completed you will recive a message soon.")

async def osu_disco(BASE, message):
	if not message.channel == message.name: return

	m = message.content.split(" ")

	confirm = await BASE.modules._Twitch_.Utils.get_opposite_osu_twitch(BASE, message.room_id, platform="twitch")

	if confirm == None:
		await BASE.Twitch_IRC_connection.send_message(message.name, "@{0} You never connected a Osu! account.".format(message.save_name))

	else:
		await BASE.Twitch_IRC_connection.send_message(message.name, "Your connection to Osu Account: {0} has been deleted".format(confirm["osu"]["name"]))
		await BASE.modules._Twitch_.Utils.delete_verify(BASE, message.room_id, platform="twitch")
