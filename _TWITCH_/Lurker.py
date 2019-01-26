import asyncio, math

# async handler loop
# called in _TWITCH_/Main_twitch.py | BASE.twitch
# as enshure corotine
async def Base(BASE):
	sleep_time = 60 * 5
	# channel_settings = kwargs.get('channel_settings', {})
	#
	# #level disabled
	# if not channel_settings.get("active_level", False):
	# 	return


	# BASE.active.twitch_stream is required, since its provides data
	while BASE.twitch.lurker_loop_running and BASE.modules._Twitch_.Streams.Main != None:
		try:
			currently_in_channel = [BASE.twitch.channels[c].id for c in BASE.twitch.channels if BASE.twitch.channels[c].id != None]
			currently_live_channels = BASE.PhaazeDB.select(of="twitch/stream", where=f"data['live'] and data['chat_managed'] and data['twitch_id'] in {str(currently_in_channel)}")
			if currently_live_channels.get("hits", 0) == 0:
				# no spectated channel is live
				await asyncio.sleep(sleep_time)
				continue

			bot_list_db = BASE.PhaazeDB.select(of="setting/known_twitch_bots")
			bot_list = [bot["name"].lower() for bot in bot_list_db['data'] if bot.get("name", None) != None]

			live_channel = currently_live_channels.get("data", [])
			for channel in live_channel:

				channel_settings = await BASE.modules._Twitch_.Utils.get_channel_settings(BASE, channel.get("twitch_id", None), prevent_new=True)
				if channel_settings != None and not channel_settings.get('active_level', False):
					continue

				twitch_bot_channel_id = channel.get("twitch_id", None)
				twitch_bot_channel = BASE.twitch.channels.get(twitch_bot_channel_id, None)
				if twitch_bot_channel == None: continue

				# NOTE: making it actully name based, because Twitch is to dumb to send ID's - Thanks
				# FIXME: Maybe sometimes fix this to ID, someday
				viewer = [ twitch_bot_channel.users[user_name].name for user_name in twitch_bot_channel.users ]
				user_to_check = BASE.PhaazeDB.select(of=f"twitch/level/level_{twitch_bot_channel_id}", where=f"data['user_name'] in {str(viewer)}", limit=len(viewer) ).get("data", [])

				#check if user has level up
				for user in user_to_check:

					#is a bot or has no name -> skip it
					if user.get("user_name", "").lower() in bot_list or user.get("user_name", "").lower() == "": continue

					#no level alert for owner -> skip it
					if twitch_bot_channel.name.lower() == user.get("user_name", "").lower():
						continue

					await check_levelup(BASE, channel_settings, twitch_bot_channel, user)

				#update all
				db_lvl_up_request = [
					"data['amount_time'] += 1;",
					f"data['amount_currency'] += {channel_settings.get('gain_currency', 1)};",
					"data['active'] -= 1 if data.get('active', 0) > 0 else 0"
				]

				BASE.PhaazeDB.update(
					of=f"twitch/level/level_{twitch_bot_channel_id}",
					where=f"str(data['user_name']) in {str(viewer)}",
					content="".join(db_lvl_up_request)
				)

				await asyncio.sleep(0.05)

			await asyncio.sleep( sleep_time )

		except Exception as e:
			BASE.modules.Console.CRITICAL("Twitch Lurker Loop cause a error\n"+str(e))
			await asyncio.sleep( sleep_time/2 )

async def check_levelup(BASE, channel_settings, channel, user):
	default_level_message = ">> [display_name] is now level [level]"

	now_level = Calc.get_lvl(user.get('amount_time', 0))
	exp_to_next = Calc.get_exp(now_level+1)

	#has a level up, and is active
	if exp_to_next == user.get('amount_time', 0)+1 and user.get("active", 0) != 0:

		#get level message
		level_message = channel_settings.get('message_level', default_level_message)
		if level_message == None:
			level_message = default_level_message

		level_message = level_message.replace( '[name]', user.get('user_name', '[N/A]') )
		level_message = level_message.replace( '[display_name]', user.get('user_display_name', '[N/A]') )
		level_message = level_message.replace( '[channel]', channel.name )
		level_message = level_message.replace( '[level]', str(now_level+1) )
		level_message = level_message.replace( '[time]',  str(round((user.get('amount_time', 0)*5) / 60, 1)) )

		asyncio.ensure_future(
			BASE.twitch.send_message( channel.name, level_message )
		)

class Calc(object):
	# calculation data and functions
	# there are not controlles in BASE.limit

	LEVEL_DEFAULT_EXP = 2
	LEVEL_MULTIPLIER = 1.2

	def get_lvl(xp: int):
		l = (-Calc.LEVEL_DEFAULT_EXP + (Calc.LEVEL_DEFAULT_EXP ** 2 - 4 * (Calc.LEVEL_DEFAULT_EXP * Calc.LEVEL_MULTIPLIER) * (-xp)) ** 0.5) / (2 * (Calc.LEVEL_DEFAULT_EXP * Calc.LEVEL_MULTIPLIER))
		return math.floor(l)

	def get_exp(lvl: int):
		l = (lvl * Calc.LEVEL_DEFAULT_EXP) + ( (Calc.LEVEL_MULTIPLIER * lvl) * (lvl * Calc.LEVEL_DEFAULT_EXP) )
		return math.floor(l)

