#BASE.modules._Twitch_.Level

import asyncio, json

cooldown_stats = []

async def Base(BASE, message, **kwargs):
	channel_settings = kwargs.get('channel_settings', None)
	if channel_settings == None:
		channel_settings = await BASE.modules._Twitch_.Utils.get_channel_settings(BASE, message.channel_id)
		kwargs['channel_settings'] = channel_settings

	# twitch stream module not loaded, means we can not know if channel is live or not
	if BASE.modules._Twitch_.Streams.Main == None:
		BASE.modules.Console.DEBUG(f"Level gain in {message.channel_name} not possible, Twitch Streams are disabled", require="twitch:level")
		return

	#level disabled
	if not channel_settings.get("active_level", False):
		return

	#only if channel is live
	if not message.channel_id in BASE.modules._Twitch_.Streams.Main.live:
		return

	#get levels
	user_level = await BASE.modules._Twitch_.Utils.get_channel_levels(BASE, message.channel_id, user_id=message.user_id)

	if len(user_level) <= 0:
		new_user = dict(
			user_id = message.user_id,
			user_name = message.name,
			user_display_name = message.display_name,
			amount_time = 1,
			amount_currency = 1,
			active = 5
		)

		BASE.PhaazeDB.insert(
			into=f'twitch/level/level_{message.channel_id}',
			content=new_user
		)

	else:
		user = user_level[0]
		c = dict(
			user_name = message.name,
			user_display_name = message.display_name,
			amount_currency = user.get('amount_currency',0) + channel_settings.get('gain_currency_message', 1),
			active = 5,
		)

		BASE.PhaazeDB.update(
			of=f"twitch/level/level_{message.channel_id}",
			content=c,
			where=f"str(data['user_id']) == str({message.user_id})",
			limit=1
		)

async def stats(BASE, message, kwargs):
	if message.channel_id in cooldown_stats: return

	#timeout this channel
	asyncio.ensure_future(timeout_stats(BASE, message.channel_id))

	channel_settings = kwargs.get('channel_settings', None)
	if channel_settings == None:
		channel_settings = await BASE.modules._Twitch_.Utils.get_channel_settings(BASE, message.channel_id)
		kwargs['channel_settings'] = channel_settings


	#level disabled
	if not channel_settings.get("active_level", False):
		return

	m = message.content[len(BASE.vars.TRIGGER_TWITCH):].split(" ")

	if len(m) == 3:
		if m[1].lower() == "calc":
			if m[2].isdigit():
				needed_time = BASE.modules._Twitch_.Lurker.Calc.get_exp(int(m[2]))
				hours = str(round((needed_time*5) / 60, 1))
				resp = f"Level {m[2]} = {hours}h+"

				return await BASE.twitch.send_message(message.channel_name, resp)

	if len(m) == 1:
		u = 0
		search_user = message.name
	else:
		u = 1
		search_user = m[1]

	user = BASE.PhaazeDB.select(
		of = f"twitch/level/level_{message.channel_id}",
		where = f"data['user_name'] == {json.dumps( str(search_user).lower() )}", limit=1,
	)

	if user.get('data', []) == []:
		if u == 1:
			return await BASE.twitch.send_message(message.channel_name, f"@{message.display_name}, no stats found for: {search_user}.")
		elif u == 0:
			return await BASE.twitch.send_message(message.channel_name, f"@{message.display_name}, sorry but you don't have stats yet.")

	user = user['data'][0]

	currency_name_multi = channel_settings.get('currency_name_multi', BASE.vars.DEFAULT_TWITCH_CURRENCY_MULTI) or BASE.vars.DEFAULT_TWITCH_CURRENCY_MULTI

	#owner
	if message.channel_name == user.get('user_name', None):
		currency = str( user.get("amount_currency", 0) )
		display_name = user.get('user_display_name', None)
		return await BASE.twitch.send_message(message.channel_name, f"{display_name}, {currency_name_multi}: {currency} | Level: ∞ (Channel Owner)")

	currency = str(user.get("amount_currency", 0))
	time = user.get("amount_time", 1) * 5
	hours = str(round(time / 60, 1))

	current_level = BASE.modules._Twitch_.Lurker.Calc.get_lvl(time/5)
	time_to_next = BASE.modules._Twitch_.Lurker.Calc.get_exp(current_level+1)
	time_to_next = str(round((time_to_next * 5) / 60, 1))

	if u == 0:
		resp = f"@{message.display_name}, {currency_name_multi}: {currency} | Level: {current_level} ({hours}h/{time_to_next}h)"
	elif u == 1:
		resp = f"Stats for: {search_user}, {currency_name_multi}: {currency} | Level: {current_level} ({hours}h/{time_to_next}h)"

	return await BASE.twitch.send_message(message.channel_name, resp)

async def leaderboard(BASE, message, kwargs): #TODO: x
	if message.channel_id in cooldown_stats: return

	#timeout this channel
	asyncio.ensure_future(timeout_stats(BASE, message.channel_id))

	# get settings
	channel_settings = kwargs.get('channel_settings', None)
	if channel_settings == None:
		channel_settings = await BASE.modules._Twitch_.Utils.get_channel_settings(BASE, message.channel_id)
		kwargs['channel_settings'] = channel_settings

	#level disabled = no leaderboard
	if not channel_settings.get("active_level", False):
		return

	m = message.content[len(BASE.vars.TRIGGER_TWITCH):].split(" ")

	search_time = True

	if len(m) >= 2:
		if m[1].lower() == "currency": search_time = False

	channel_level_stats = await BASE.modules._Twitch_.Utils.get_channel_levels(BASE, message.channel_id)

	if search_time:
		sort_list = sorted(channel_level_stats, key=lambda user: user.get("amount_time", 0), reverse=True)
	else:
		sort_list = sorted(channel_level_stats, key=lambda user: user.get("amount_currency", 0), reverse=True)

	return_list = []
	check_size = 3 if len(sort_list) > 3 else len(sort_list)

	for x in range(check_size):
		user = sort_list[x]
		place = x+1
		name = user.get("user_display_name", "[N/A]")
		if search_time:
			time = user.get("amount_time", 0)
			calc_time = str( round( (time*5)/60, 1) )
			return_list.append(f"#{place}: {name} [{calc_time}h]")
		else:
			currency = user.get("amount_currency", 0)
			return_list.append(f"#{place}: {name} [{currency}]")

	aws = " | ".join(x for x in return_list)

	return await BASE.twitch.send_message(message.channel_name, aws + f" (https://phaaze.net/twitch/level/{message.channel_name})")

async def timeout_stats(BASE, room_id):
	cooldown_stats.append(room_id)
	await asyncio.sleep(BASE.limit.TWITCH_STATS_COOLDOWN)
	cooldown_stats.remove(room_id)

