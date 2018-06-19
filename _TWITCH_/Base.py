#BASE.modules._Twitch_.Base

import asyncio, json

async def on_message(BASE, message):

	# NOTE: -
	# PhaazeDB can handle ~700 request/sec without a big delay.
	# Discord traffic at highest: ~200 request/s calculated with 5M+ Users
	# means there are ~500 request/s left, based on twitchstatus.com we have ~ 900-1000 msg/s on ALL channels
	# calculated with 200 - 400 channels (~5-20 msg/s) should not be a huge problem and have space for PhaazeWeb and more

	channel_settings = await BASE.modules._Twitch_.Utils.get_channel_settings(BASE, message.channel_id)
	channel_commands = await BASE.modules._Twitch_.Utils.get_channel_commands(BASE, message.channel_id)
	#channel_levels =   await BASE.modules._Twitch_.Utils.get_channel_levels(BASE, message.channel.id)
	#channel_quotes =   await BASE.modules._Twitch_.Utils.get_channel_quotes(BASE, message.channel.id)

	#blacklist (Only, when links are banned or at least one word is in the blacklist AND there is a purge/timeout)
	if channel_settings.get("blacklist_punishment", 0) != 0 and (channel_settings.get('ban_links', False) or channel_settings.get('blacklist', []) != []):
		await BASE.modules._Twitch_.Blacklist.check(BASE, message, channel_settings)

	return #TODO: later
	await BASE.modules._Twitch_.Custom.get(BASE, message, channel_settings=channel_settings, channel_commands=channel_commands)

	if message.content.startswith('!'):
		pass

	"""Phaaze Commands"""



async def on_member_join(BASE, channel, name):
	for chan in BASE.Twitch_IRC_connection.channels:
		if chan.name.lower() == channel.lower():
			_chan_ = chan
			break

	if not name.lower() in [n for n in _chan_.user]:
		_chan_.user.append(name.lower())

async def on_member_leave(BASE, channel, name):
	for chan in BASE.Twitch_IRC_connection.channels:
		_chan_ = None
		if chan.name.lower() == channel.lower():
			_chan_ = chan
			break

	if _chan_ == None:
		return

	if name.lower() in [n for n in _chan_.user]:
		_chan_.user.remove(name.lower())

async def on_sub(BASE, sub):
	default_sub_message = "PogChamp [name] just subscribed! Thanks [name]"
	default_resub_message = "PogChamp [name] just subscribed for [months] months in a row! Thanks for the continued support [name] <3"
	settings = await BASE.modules._Twitch_.Utils.get_twitch_file(BASE, sub.room_id)

	if settings.get('sub_alert', False) == True or sub.channel == "the__cj":

		sub_message = settings.get('sub_message', None)
		if sub_message == None:
			sub_message = default_sub_message

			sub_message = sub_message.replace('[name]', sub.display_name)

		await BASE.Twitch_IRC_connection.send_message(sub.channel, sub_message)

class Settings(object):

	available = ["stats", "quotes", "game", "osu"]
	error_message = "Unknown option, to turn off/on options use \"!settings [option] [on|off]\""

	async def Base(BASE, message):
		if not (message.channel == message.name or message.mod): return

		m = message.content.split(" ")

		if len(m) == 1:
			return await BASE.Twitch_IRC_connection.send_message(message.channel, "@{0}, available setting options: {1}".format(message.save_name, ", ".join(f for f in Settings.available)))

		if not m[1].lower() in Settings.available:
			return await BASE.Twitch_IRC_connection.send_message(message.channel, "@{0}, unknown option > available: {1}".format(message.save_name, ", ".join(f for f in Settings.available)))

		if m[1].lower() == "stats":
			await Settings.Stats(BASE, message)

		if m[1].lower() == "quotes":
			await Settings.Quotes(BASE, message)

		if m[1].lower() == "game":
			await Settings.Game(BASE, message)

		if m[1].lower() == "osu":
			await Settings.Osu(BASE, message)

	async def Stats(BASE, message):
		settings = await BASE.modules._Twitch_.Utils.get_twitch_file(BASE, message.room_id)
		settings["stats"] = settings.get("stats", False)
		m = message.content.split(" ")

		if len(m) == 2:
			return await BASE.Twitch_IRC_connection.send_message(
				message.channel,
				"Quotes are currently: {0}".format("Enabled" if settings['games'] else "Disabled"))

		if m[2].lower() in ['no', 'disable', 'off']:
			settings["stats"] = False
			with open("_TWITCH_/Channel_files/{0}.json".format(message.room_id), "w") as new:
				json.dump(settings, new)
				setattr(BASE.twitchfiles, "channel_"+message.room_id, settings)
				await BASE.Twitch_IRC_connection.send_message(
					message.channel,
					"Watch and Credit stats disabled")

		elif m[2].lower() in ['yes', 'enable', 'on']:
			settings["stats"] = True
			with open("_TWITCH_/Channel_files/{0}.json".format(message.room_id), "w") as new:
				json.dump(settings, new)
				setattr(BASE.twitchfiles, "channel_"+message.room_id, settings)
				await BASE.Twitch_IRC_connection.send_message(
					message.channel,
					"Watch and Credit stats enabled")
		else:
			return await BASE.Twitch_IRC_connection.send_message(
				message.channel,
				Settings.error_message)

	async def Quotes(BASE, message):
		settings = await BASE.modules._Twitch_.Utils.get_twitch_file(BASE, message.room_id)
		settings["quote_active"] = settings.get("quote_active", False)
		m = message.content.split(" ")

		if len(m) == 2:
			return await BASE.Twitch_IRC_connection.send_message(
				message.channel,
				"Quotes are currently: {0}".format("Enabled" if settings['games'] else "Disabled"))

		if m[2].lower() in ['no', 'disable', 'off']:
			settings["quote_active"] = False
			with open("_TWITCH_/Channel_files/{0}.json".format(message.room_id), "w") as new:
				json.dump(settings, new)
				setattr(BASE.twitchfiles, "channel_"+message.room_id, settings)
				await BASE.Twitch_IRC_connection.send_message(
					message.channel,
					"Quotes disabled")

		elif m[2].lower() in ['yes', 'enable', 'on']:
			settings["quote_active"] = True
			with open("_TWITCH_/Channel_files/{0}.json".format(message.room_id), "w") as new:
				json.dump(settings, new)
				setattr(BASE.twitchfiles, "channel_"+message.room_id, settings)
				await BASE.Twitch_IRC_connection.send_message(
					message.channel,
					"Quotes enabled")
		else:
			return await BASE.Twitch_IRC_connection.send_message(
				message.channel,
				Settings.error_message)

	async def Game(BASE, message):
		settings = await BASE.modules._Twitch_.Utils.get_twitch_file(BASE, message.room_id)
		settings["games"] = settings.get("games", False)
		m = message.content.split(" ")

		if len(m) == 2:
			return await BASE.Twitch_IRC_connection.send_message(
				message.channel,
				"Games are currently: {0}".format("Enabled" if settings['games'] else "Disabled"))

		if m[2].lower() in ['no', 'disable', 'off']:

			settings["games"] = False
			with open("_TWITCH_/Channel_files/{0}.json".format(message.room_id), "w") as new:
				json.dump(settings, new)
				setattr(BASE.twitchfiles, "channel_"+message.room_id, settings)
				await BASE.Twitch_IRC_connection.send_message(
					message.channel,
					"Chat Games disabled")

		elif m[2].lower() in ['yes', 'enable', 'on']:

			settings["games"] = True
			with open("_TWITCH_/Channel_files/{0}.json".format(message.room_id), "w") as new:
				json.dump(settings, new)
				setattr(BASE.twitchfiles, "channel_"+message.room_id, settings)
				await BASE.Twitch_IRC_connection.send_message(
					message.channel,
					"Chat Games enabled")

		else:
			return await BASE.Twitch_IRC_connection.send_message(
				message.channel,
				Settings.error_message)

	async def Osu(BASE, message):
		settings = await BASE.modules._Twitch_.Utils.get_twitch_file(BASE, message.room_id)
		settings["osu"] = settings.get("osu", False)
		m = message.content.split(" ")

		if len(m) == 2:
			return await BASE.Twitch_IRC_connection.send_message(
				message.channel,
				"Games are currently: {0}".format("Enabled" if settings.get('games', False) else "Disabled"))

		if m[2].lower() in ['no', 'disable', 'off']:
			settings["osu"] = False
			with open("_TWITCH_/Channel_files/{0}.json".format(message.room_id), "w") as new:
				json.dump(settings, new)
				setattr(BASE.twitchfiles, "channel_"+message.room_id, settings)
				await BASE.Twitch_IRC_connection.send_message(
					message.channel,
					"Osu! interation disabled")

		elif m[2].lower() in ['yes', 'enable', 'on']:
			settings["osu"] = True
			with open("_TWITCH_/Channel_files/{0}.json".format(message.room_id), "w") as new:
				json.dump(settings, new)
				setattr(BASE.twitchfiles, "channel_"+message.room_id, settings)
				await BASE.Twitch_IRC_connection.send_message(
					message.channel,
					"Osu! interation enabled")
		else:
			return await BASE.Twitch_IRC_connection.send_message(
				message.channel,
				Settings.error_message)

class Commands(object):

	async def check_commands(BASE, message):
		m = message.content.lower().split(" ")
		trigger = m[0][1:]

		if trigger.startswith("!!!!"):
			if message.name != "the__cj": return
			await BASE.modules._Twitch_.Utils.debug(BASE, message)

		elif trigger.startswith("setting"):
			await BASE.modules._Twitch_.Base.Settings.Base(BASE, message)

		elif trigger.startswith("battle"):
			await BASE.modules._Twitch_.Games.battle(BASE, message)

		elif trigger.startswith("mission"):
			await BASE.modules._Twitch_.Games.mission(BASE, message)

		elif trigger.startswith("stats"):
			await BASE.modules._Twitch_.Gold.stats(BASE, message)

		elif trigger.startswith("toptime"):
			await BASE.modules._Twitch_.Gold.leaderboard(BASE, message, locals(), art="time")

		elif trigger.startswith("topmoney"):
			await BASE.modules._Twitch_.Gold.leaderboard(BASE, message, locals(), art="money")

		elif trigger.startswith("quote"):
			await BASE.modules._Twitch_.CMD.Normal.Quote(BASE, message)

		elif trigger.startswith("addquote"):
			await BASE.modules._Twitch_.CMD.Mods.Quotes.add(BASE, message)

		elif trigger.startswith("delquote"):
			await BASE.modules._Twitch_.CMD.Mods.Quotes.rem(BASE, message)

		elif trigger.startswith("addcom"):
			await BASE.modules._Twitch_.CMD.Mods.Coms.add(BASE, message)

		elif trigger.startswith("delcom"):
			await BASE.modules._Twitch_.CMD.Mods.Coms.rem(BASE, message)

		elif trigger.startswith("osuverify"):
			await BASE.modules._Twitch_.CMD.Mods.verify(BASE, message)

		elif trigger.startswith("osudisconnect"):
			await BASE.modules._Twitch_.CMD.Mods.osu_disco(BASE, message)

		elif trigger.startswith("join"):
			await BASE.modules._Twitch_.Base.Commands.join(BASE, message)

		elif trigger.startswith("leave"):
			await BASE.modules._Twitch_.Base.Commands.leave(BASE, message)

	async def leave(BASE, message):
		if message.save_name.lower() == message.channel.lower() or \
			message.type == "admin" or \
			message.type == "staff" or \
			message.save_name.lower() == BASE.Twitch_IRC_connection.owner.lower():

			if message.channel.lower() == BASE.Twitch_IRC_connection.nickname.lower():
				return

			await BASE.Twitch_IRC_connection.send_message(message.channel, "Phaaze will leave the channel")

			file = json.loads(open("_TWITCH_/_achtive_channels.json", "r").read())
			file.get("channels", []).remove(message.channel.lower())
			with open("_TWITCH_/_achtive_channels.json", "w") as save:
				json.dump(file, save)
				await BASE.Twitch_IRC_connection.part_channel(message.channel)

	async def join(BASE, message):
		if BASE.Twitch_IRC_connection.nickname.lower() != message.channel.lower():
			return

		file = json.loads(open("_TWITCH_/_achtive_channels.json", "r").read())
		if message.name.lower() in file.get("channels", []):
			return await BASE.Twitch_IRC_connection.send_message(message.channel, "Phaaze already is in your channel.")
		else:
			file.get("channels", []).append(message.name.lower())
			await BASE.Twitch_IRC_connection.send_message(message.channel, "Phaaze has joined your channel. :D")
			with open("_TWITCH_/_achtive_channels.json", "w") as save:
				json.dump(file, save)
				await BASE.Twitch_IRC_connection.join_channel(message.name)

#async handler loop
async def lurkers(BASE):
	sleep_time = 60 * 5

	while True:
		to_check = ",".join(channel.room_id for channel in BASE.Twitch_IRC_connection.channels)
		url = "https://api.twitch.tv/kraken/streams?channel=" + to_check
		check = await BASE.modules._Twitch_.Utils.twitch_API_call(BASE, url)
		if check.get("status", 200) > 400:
			await asyncio.sleep(10)
			continue

		found = [str(stream["channel"]["_id"]) for stream in check["streams"]]
		for check_live in BASE.Twitch_IRC_connection.channels:
			if check_live.room_id in found:
				check_live.live = True
			else:
				check_live.live = False

		for channel in BASE.Twitch_IRC_connection.channels:
			if not channel.live:
				continue
			try:
				level_file = await BASE.modules._Twitch_.Utils.get_twitch_level_file(BASE, channel.room_id)
				level_file["user"] = level_file.get("user", [])

				check_if_in_stream = [u for u in channel.user]

				for user in level_file["user"]:
					if user["name"] in check_if_in_stream:
						user["time"] += 1
						user["amount"] += 10

						user["active"] = user.get("active", 0)
						if user["active"] > 0:
							user["active"] -= 1
					else:
						user["active"] = user.get("active", 0)
						if user["active"] > 0:
							user["active"] = 0

					now_level = await Calc.get_lvl(user["time"])
					exp_to_next = await Calc.get_exp(now_level)

					if exp_to_next == user["time"] and user["active"] != 0:
						await BASE.Twitch_IRC_connection.send_message(channel.name, ">> {0} is now {2} level {1}".format(user["call_name"], str(now_level+1), channel.name))
						user["time"] += 1

				with open("_TWITCH_/Channel_level_files/{0}.json".format(channel.room_id), "w") as save:
					setattr(BASE.twitchlevelfiles, "channel_"+channel.room_id, level_file)
					json.dump(level_file, save)

				await asyncio.sleep(0.05)
			except:
				pass

		await asyncio.sleep( sleep_time )

class Calc(object):

	async def get_exp(lvl):
		return round( 4 + ((lvl * 3) + (lvl * (lvl * 3) * 2)) )

	async def get_lvl(exp):
		lvl = 0
		while await Calc.get_exp(lvl) < exp:
			lvl += 1
		return lvl

async def timeout_command(name):
	custom_commands_in_last_15s.append(name)
	await asyncio.sleep(15)
	custom_commands_in_last_15s.remove(name)
