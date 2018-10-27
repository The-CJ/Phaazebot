##BASE.modules._Twitch_.Blacklist

import asyncio, re, Regex

blacklist_channel_cooldown = []
already_known_incidents_L1 = []
already_known_incidents_L2 = []

async def check(BASE, message, channel_settings):
	#ignore mods
	if await BASE.modules._Twitch_.Utils.is_Mod(BASE, message):	return

	blacklist = channel_settings.get("blacklist", [])
	ban_links = channel_settings.get("ban_links", False)
	link_whitelist = channel_settings.get("link_whitelist", [])

	for word in blacklist:
		if word.lower() in message.content.lower():
			return await punish(BASE, message, channel_settings, reason="word")

	if ban_links:
		found_links = re.finditer(Regex.contains_link, message.content)
		if found_links != None:

			for hit in found_links:
				p = True

				for white_link in link_whitelist:
					if re.search(white_link, hit.group(0)) != None:
						p = False
						break

				if p:
					return await punish(BASE, message, channel_settings, reason="link")

async def punish(BASE, message, channel_settings, reason="word"):
	punishment_level = channel_settings.get("blacklist_punishment", 0)

	#should not happen
	if punishment_level == 0: return

	if reason == "link":
		m = channel_settings.get('blacklist_link_message', None)
	else:
		m = channel_settings.get('blacklist_message', None)

	if m not in [None, "", " "]:
		m = m.replace('{display_name}', message.display_name)
		m = m.replace('{name}', message.name)
		m = m.replace('{user_id}', message.user_id)
	else:
		#default message
		if reason == "link":
			m = f"Hey there @{message.display_name}, stop posting links without permission."
		else:
			m = f"Sorry @{message.display_name}, what have you said?."

	# set punishmet multiplyer
	uid = f"{message.channel_id}_{message.user_id}"
	if uid in already_known_incidents_L2:
		warn_level = 3

	elif uid in already_known_incidents_L1:
		already_known_incidents_L2.append(uid)
		asyncio.ensure_future(remove_from_known_incidents_L2(uid, BASE.limit.TWITCH_BLACKLIST_REMEMBER_TIME), loop=BASE.Worker_loop)
		warn_level = 2
		m = m + " [Last Warning]"

	else:
		already_known_incidents_L1.append(uid)
		asyncio.ensure_future(remove_from_known_incidents_L1(uid. BASE.limit.TWITCH_BLACKLIST_REMEMBER_TIME), loop=BASE.Worker_loop)
		warn_level = 1
		m = m + " [Warning]"

	#send a message to warn the user, but dont spam it
	if not message.channel_id in blacklist_channel_cooldown and channel_settings.get("blacklist_notify", False):
		try:
			asyncio.ensure_future(blacklist_cooldown(BASE, message.channel_id))
			await BASE.twitch.send_message(message.channel_name, m)
		except:
			pass

	if warn_level == 3:
		return await BASE.twitch.send_message(message.channel_name, f"/ban {message.name}")

	elif warn_level == 2:
		timeout_time = punishment_level * warn_level
		return await BASE.twitch.send_message(message.channel_name, f"/timeout {message.name} {timeout_time}")

	else:
		return await BASE.twitch.send_message(message.channel_name, f"/timeout {message.name} {punishment_level}")

async def blacklist_cooldown(BASE, channel_id):
	#gets called after a channel got a ban/timeout message,
	#so phaaze won't spam a channel but timeouts user
	blacklist_channel_cooldown.append(channel_id)
	await asyncio.sleep(BASE.limit.TWITCH_TIMEOUT_MESSAGE_COOLDOWN)
	blacklist_channel_cooldown.remove(channel_id)

async def remove_from_known_incidents_L1(uid, remember):
	await asyncio.sleep(remember)
	already_known_incidents_L1.remove(uid)

async def remove_from_known_incidents_L2(uid, remember):
	await asyncio.sleep(remember)
	already_known_incidents_L2.remove(uid)