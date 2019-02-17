#BASE.modules._Twitch_.Level

import asyncio, json

cooldown_stats = []

async def Base(BASE, message, **kwargs):
	channel_settings = kwargs.get('channel_settings', {})

	# twitch stream module not loaded, means we can not know if channel is live or not
	if BASE.modules._Twitch_.Streams.Main == None:
		BASE.modules.Console.DEBUG(f"Level gain in {message.channel_name} not possible, Twitch Streams are disabled", require="twitch:level")
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

async def leaderboard(BASE, message, package, art="time"): #TODO: x
	settings = await package["BASE"].moduls._Twitch_.Utils.get_twitch_file(package["BASE"], package["message"].room_id)
	stats_active = settings.get("stats", False)
	if not stats_active: return

	def get_lenght(check):
		if check.isdigit():
			if 0 < int(check) < 6:
				return int(check)
		else:
			return 3

	if len(package["m"]) >= 2:
		number = get_lenght(package["m"][1])
	else:
		number = 3

	level_file = await package["BASE"].moduls._Twitch_.Utils.get_twitch_level_file(package["BASE"], package["message"].room_id)
	all_user = level_file.get("user", [])

	if art == "time":
		cool_list = sorted(all_user, key=lambda user: user["time"], reverse=True)
	elif art == "money":
		cool_list = sorted(all_user, key=lambda user: user["amount"], reverse=True)
	else:
		return

	end_list = []
	start_count = 0
	for user in cool_list:
		if start_count == number:
			break

		try:
			if user["name"].lower() == message.channel:
				continue
			if user["name"].lower() in BASE.vars.twitch_bots:
				continue

			N = user["call_name"]
			A = str(user["amount"])
			T = str( round( (user["time"]*5)/60, 1) )
			NU = str(start_count+1)

			end_list.append("#{3}: {0} [{2}h - {1} C]".format(N, A, T, NU))
			start_count += 1
		except:
			continue

	return await BASE.Twitch_IRC_connection.send_message(message.channel, " | ".join(x for x in end_list))

async def timeout_stats(BASE, room_id):
	cooldown_stats.append(room_id)
	await asyncio.sleep(BASE.limit.TWITCH_STATS_COOLDOWN)
	cooldown_stats.remove(room_id)

