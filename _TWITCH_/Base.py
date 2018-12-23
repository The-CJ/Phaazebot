#BASE.modules._Twitch_.Base

import asyncio, math

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

	#osu link
	if channel_settings.get('linked_osu_account', None) != None:
		await BASE.modules._Twitch_.PROCESS.Normal.OsuRequests.Base(BASE, message, channel_settings=channel_settings)

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

# async handler loop
# called in _TWITCH_/Main_twitch.py | BASE.twitch
async def lurkers(BASE):
	sleep_time = 60 * 5

	# BASE.active.twitch_stream is required, since its provides data
	while BASE.twitch.lurker_loop_running and BASE.active.twitch_stream:
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
					"data['active'] -= 1 if data.get('active', 0) else 0"
				]

				BASE.PhaazeDB.update(
					of=f"twitch/level/level_{twitch_bot_channel_id}",
					where=f"str(data['user_name']) in {str(viewer)}",
					content="".join(db_lvl_up_request)
				)

				await asyncio.sleep(0.05)

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

