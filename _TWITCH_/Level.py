#BASE.modules._Twitch_.Level

import asyncio

async def Base(BASE, message, **kwargs):
	channel_settings = kwargs.get('channel_settings', {})

	#not for owner
	if message.channel_name == message.name:
		return

	#only if channel is live
	if not message.channel_id in BASE.twitch.live and False: # DEBUG: testing
		return

	#get levels
	channel_levels = await BASE.modules._Twitch_.Utils.get_channel_levels(BASE, message.channel_id)

	# IDEA: add a DB function that updates if there, else create

	user = None

	for check_user in channel_levels:
		if check_user.get('user_id', None) == message.user_id:
			user = check_user

	if user == None:
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
		c = dict(
			user_name = message.name,
			user_display_name = message.display_name,
			amount_currency = user.get('amount_currency',0) + channel_settings.get('gain_currency_message', 1),
			active = 5,
		)

		BASE.PhaazeDB.update(
			of=f"twitch/level/level_{message.channel_id}",
			content=c,
			where=f"str(data['user_id']) == str({message.user_id})"
		)

async def stats(BASE, message):
	if message.room_id in asked_stats: return
	asyncio.ensure_future(timeout_stats(message.room_id))

	settings = await BASE.modules._Twitch_.Utils.get_twitch_file(BASE, message.room_id)
	stats_active = settings.get("stats", False)
	if not stats_active: return

	level_file = await BASE.modules._Twitch_.Utils.get_twitch_level_file(BASE, message.room_id)
	all_user = level_file.get("user", [])

	m = message.content.split(" ")
	if len(m) == 1:

		author = await get_user(BASE, all_user, message.user_id)

		#owner
		if message.channel == message.name:
			gold = str(author.get("amount", 0))
			return await BASE.Twitch_IRC_connection.send_message(message.channel, "@{0}, Credits: {1} | Level: ∞ (Channel Owner)".format(message.save_name, str(gold)))

		#none found
		if author == None:
			return await BASE.Twitch_IRC_connection.send_message(message.channel, "@{0}, sorry but you don't have stats yet.".format(message.save_name))

		else:
			gold = str(author.get("amount", 0))

			time_in_min = author.get("time", 1) * 5
			hours = str(round(time_in_min / 60, 1))

			lvl_oder_so = str(await BASE.modules._Twitch_.Base.Calc.get_lvl(author["time"]))
			ttlvlup = await BASE.modules._Twitch_.Base.Calc.get_exp(int(lvl_oder_so))
			time_to_next = str(round((ttlvlup * 5) / 60, 1))

			resp = "@{0}, Credits: {2} | Level: {3} ({1}h/{4}h)".format(message.save_name, hours, gold, lvl_oder_so, time_to_next)
			return await BASE.Twitch_IRC_connection.send_message(message.channel, resp)

	else:
		search_term = m[1]

		found_user = await get_user(BASE, all_user, search_term.lower(), method="name")

		# already existing Twitch bots ignore
		if found_user["name"] in BASE.vars.twitch_bots: return

		if found_user == None:
			return await BASE.Twitch_IRC_connection.send_message(message.channel, "@{0}, no stats found for: {1}.".format(message.save_name, search_term))

		if found_user["name"] == message.channel:
			gold = str(found_user.get("amount", 0))
			return await BASE.Twitch_IRC_connection.send_message(message.channel, "Stats for: {0}, Credits: {1} | Level: ∞ (Channel Owner)".format(found_user["call_name"], str(gold)))

		else:
			gold = str(found_user.get("amount", 0))

			time_in_min = found_user.get("time", 1) * 5
			hours = str(round(time_in_min / 60, 1))

			lvl_oder_so = str(await BASE.modules._Twitch_.Base.Calc.get_lvl(found_user["time"]))
			ttlvlup = await BASE.modules._Twitch_.Base.Calc.get_exp(int(lvl_oder_so))
			time_to_next = str(round((ttlvlup * 5) / 60, 1))

			resp = "Stats for: {0}, Credits: {2} | Level: {3} ({1}h/{4}h)".format(found_user["call_name"], hours, gold, lvl_oder_so, time_to_next)
			return await BASE.Twitch_IRC_connection.send_message(message.channel, resp)

async def leaderboard(BASE, message, package, art="time"):
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
