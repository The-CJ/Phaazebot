#BASE.modules._Twitch_.Base

import asyncio

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

	#Phaaze Commands
	if message.content.startswith(BASE.vars.TRIGGER_TWITCH):
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

#async handler loop
async def lurkers(BASE):
	default_level_message = ">> {display_name} is now level {level}"
	sleep_time = 60 * 5

	while BASE.twitch.lurker_loop_running:
		to_check = []
		for c in BASE.twitch.channels:
			channel = BASE.twitch.channels[c]
			if channel.id != None:
				to_check.append( channel.id )

		check = BASE.modules._Twitch_.Utils.get_streams(BASE, to_check)

		# we got nothing... mean API is down
		if check == None:
			await asyncio.sleep(30)
			continue

		live_streams = check.get('streams', [])
		BASE.twitch.live = [str(stream.get('channel', {}).get('_id', None)) for stream in live_streams]

		bot_list_db = BASE.PhaazeDB.select(of="setting/known_twitch_bots")
		bot_list = [bot.get[""] for bot in bot_list_db['data'] if bot.get("name", None) != None]

		for channel_id in BASE.twitch.channels:
			channel = BASE.twitch.channels[channel_id]

			if not channel.id in BASE.twitch.live:
				continue

			try:
				channel_settings = await BASE.modules._Twitch_.Utils.get_channel_settings(BASE, channel.id)

				#channel has levels disabled
				if not channel_settings.get('active_level', False):
					continue

				channel_levels = await BASE.modules._Twitch_.Utils.get_channel_levels(BASE, channel.id)

				# NOTE: making it actully name based, because Twitch is to dumb to send ID's - Thanks
				# FIXME: Maybe sometimes fix this to ID
				viewers = [channel.users[user_name].name for user_name in channel.users]
				update_user_watch = []

				#check if user has level up
				for user in channel_levels:

					#is a bot, skip it
					if user.get("user_name", None) in bot_list: continue

					#is currently viewing, add to gain time
					if user.get("user_name", None) in viewers:
						update_user_watch.append(user.get('user_id', None))
					else:
						continue

					#no level alert for owner
					if channel.name.lower() == user.get("user_name", "").lower():
						continue

					now_level = Calc.get_lvl(user.get('amount_time', 0)+1)
					exp_to_next = Calc.get_exp(now_level)

					#has a new level
					if exp_to_next == user.get('amount_time', 0)+1 and user.get("active", 0) != 0:

						#get level message
						level_message = channel_settings.get('message_level', default_level_message)
						if level_message == None:
							level_message = default_level_message

						level_message = level_message.replace( '{display_name}', user.get('user_display_name', '[N/A]') )
						level_message = level_message.replace( '{name}', user.get('user_name', '[N/A]') )
						level_message = level_message.replace( '{level}', str(now_level+1) )
						level_message = level_message.replace( '{time}',  str(round((user.get('amount_time', 0)*5) / 60, 1)) )

						asyncio.ensure_future(
							BASE.twitch.send_message( channel.name, level_message )
						)
				BASE.PhaazeDB.update(
					of=f"twitch/level/level_{channel.id}",
					where=f"str(data['user_id']) in {str(update_user_watch)}",
					content=f"data['amount_time'] += 1; data['amount_currency'] += {channel_settings.get('gain_currency', 1)}; data['active'] -= 1 if data.get('active', 0) else 0")

				await asyncio.sleep(0.05)
			except:
				BASE.modules.Console.CRITICAL("Twitch Lurker Loop cause a unknown error")
				await asyncio.sleep( sleep_time/2 )

		await asyncio.sleep( sleep_time )

class Calc(object):

	def get_exp(lvl):
		return round( 4 + ((lvl * 3) + (lvl * (lvl * 3) * 2)) )

	def get_lvl(exp):
		lvl = 0
		while Calc.get_exp(lvl) < exp:
			lvl += 1
		return lvl

