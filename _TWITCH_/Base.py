#BASE.modules._Twitch_.Base

import asyncio, json

async def on_message(BASE, message):

	# NOTE: -
	# PhaazeDB can handle ~700 request/sec without a big delay.
	# Discord traffic at highest: ~200 request/s calculated with 5M+ Users
	# means there are ~500 request/s left, based on twitchstatus.com we have ~ 900-1000 msg/s on ALL channels
	# calculated with 200 - 400 channels (~5-20 msg/s) should not be a huge problem and have space for PhaazeWeb and more

	channel_settings = await BASE.modules._Twitch_.Utils.get_channel_settings(BASE, message.channel_id)

	#blacklist (Only, when links are banned or at least one word is in the blacklist AND there is a purge/timeout)
	if channel_settings.get("blacklist_punishment", 0) != 0 and (channel_settings.get('ban_links', False) or channel_settings.get('blacklist', []) != []):
		await BASE.modules._Twitch_.Blacklist.check(BASE, message, channel_settings)

	#custom command
	if channel_settings.get('active_custom', False):
		channel_commands = await BASE.modules._Twitch_.Utils.get_channel_commands(BASE, message.channel_id)
		if len(channel_commands) != 0:
			await BASE.modules._Twitch_.Custom.get(BASE, message, channel_settings=channel_settings, channel_commands=channel_commands)

	#level
	if channel_settings.get('active_level', False):
		await BASE.modules._Twitch_.Level.Base(BASE, message, channel_settings=channel_settings)

	#todo in function
	# channel_quotes = await BASE.modules._Twitch_.Utils.get_channel_quotes(BASE, message.channel.id)

	#Phaaze Commands
	if message.content.startswith('!'):
		if message.channel_name.lower() == BASE.twitch.nickname.lower():
		#phaaze channel only
			await BASE.modules._Twitch_.CMD.Normal.Main_channel(BASE, message, channel_settings=channel_settings)

		if await BASE.modules._Twitch_.Utils.is_Owner(BASE, message):
		#owner
			await BASE.modules._Twitch_.CMD.Owner.Base(BASE, message, channel_settings=channel_settings)

		if await BASE.modules._Twitch_.Utils.is_Mod(BASE, message):
		#mod
			await BASE.modules._Twitch_.CMD.Mod.Base(BASE, message, channel_settings=channel_settings)

		#normal
		await BASE.modules._Twitch_.CMD.Normal.Base(BASE, message, channel_settings=channel_settings)


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

