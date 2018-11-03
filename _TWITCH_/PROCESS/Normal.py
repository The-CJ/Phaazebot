#BASE.modules._TWITCH_.PROCCESS.Normal

import asyncio, random, re, Regex

class Quote(object):

	custom_quote_cooldown = []

	async def Base(BASE, message, kwargs):
		#channel still in cooldown
		if message.channel_id in Quote.custom_quote_cooldown: return
		asyncio.ensure_future(Quote.cooldown(message.channel_id))

		channel_settings = kwargs.get('channel_settings', None)
		if channel_settings == None:
			channel_settings = await BASE.modules._Twitch_.Utils.get_channel_settings(BASE, message.channel_id)

		if not channel_settings.get('active_quotes', False): return

		channel_quotes = kwargs.get('channel_quotes', None)
		if channel_quotes == None:
			channel_quotes = await BASE.modules._Twitch_.Utils.get_channel_quotes(BASE, message.channel_id)

		if len(channel_quotes) == 0:
			return await BASE.twitch.send_message(message.channel_name, 'This channel has no quotes.')

		index = None
		m = message.content[len(BASE.vars.TRIGGER_TWITCH):].split(" ")
		if len(m) > 1:
			if m[1].isdigit():
				index = int(m[1])

		if index == None:
			index = random.choice([q.get('id', None) for q in channel_quotes])

		quote = None
		for quo in channel_quotes:
			if index == quo.get('id', None):
				quote = quo.get('content', '[N/A]')
				break

		if quote == None:
			return await BASE.twitch.send_message(message.channel_name, f"Quote '{str(index)}' was not found")

		return await BASE.twitch.send_message(message.channel_name, quote + f" [ID: {str(index)}]")

	async def cooldown(channel_id, cooldown=10):
		Quote.custom_quote_cooldown.append(channel_id)
		await asyncio.sleep(cooldown)
		Quote.custom_quote_cooldown.remove(channel_id)

class OsuRequests(object):

	OSU_DOWNLOADLINK_FORMAT = "http://osu.ppy.sh/b/{id}"
	DEFAULT_CHAT_RESPONSE_OSU = "[{osu_link} {title} [{version}]] ★ {stars} | Lenght: {lenght}min | BPM: {bpm} | mapped by {creator}, | requested by {requester}"
	DEFAULT_CHAT_RESPONSE_TWITCH = "{artist} | {title} [{version}] mapped by {creator} | ★ {stars} | Lenght: {lenght}min | BPM: {bpm}"

	async def Base(BASE, message, **kwargs):
		channel_settings = kwargs.get('channel_settings', None)
		if channel_settings == None:
			channel_settings = await BASE.modules._Twitch_.Utils.get_channel_settings(BASE, message.channel_id)

		osu_user = channel_settings.get('linked_osu_account', None)
		if osu_user == None: return # should never happen, just to be sure

		osu_map_link = re.match(Regex.Osu.maplink, message.content)
		if osu_map_link == None: return # nothing found

		searchmode = "b" if osu_map_link.group('id2') != None else "s"
		searchid = osu_map_link.group('id2') or osu_map_link.group('id1')

		map_result = await BASE.modules._Osu_.Utils.get_maps(BASE, ID=searchid, mode=searchmode)
		if map_result == None: print("FIXME"); return

		display_map = map_result.all_maps[0]

		chat_response_osu = channel_settings.get('osurequestformat_osu', None) or OsuRequests.DEFAULT_CHAT_RESPONSE_OSU
		chat_response_twitch = channel_settings.get('osurequestformat_twitch', None) or OsuRequests.DEFAULT_CHAT_RESPONSE_TWITCH

		# replace everything TODO: find a better method

		odf = OsuRequests.OSU_DOWNLOADLINK_FORMAT.format( id=display_map.map_id )

		chat_response_osu = chat_response_osu.replace("{artist}",    str(display_map.artist) )
		chat_response_osu = chat_response_osu.replace("{title}",     str(display_map.title) )
		chat_response_osu = chat_response_osu.replace("{version}",   str(display_map.version) )
		chat_response_osu = chat_response_osu.replace("{stars}",     str(round(display_map.diff,2)) )
		chat_response_osu = chat_response_osu.replace("{lenght}",    str(display_map.lenght))
		chat_response_osu = chat_response_osu.replace("{bpm}",       str(display_map.bpm))
		chat_response_osu = chat_response_osu.replace("{creator}",   str(display_map.creator))
		chat_response_osu = chat_response_osu.replace("{requester}", str(message.display_name))
		chat_response_osu = chat_response_osu.replace("{osu_link}",  str(odf))

		chat_response_twitch = chat_response_twitch.replace("{artist}",    str(display_map.artist) )
		chat_response_twitch = chat_response_twitch.replace("{title}",     str(display_map.title) )
		chat_response_twitch = chat_response_twitch.replace("{version}",   str(display_map.version) )
		chat_response_twitch = chat_response_twitch.replace("{stars}",     str(round(display_map.diff,2)) )
		chat_response_twitch = chat_response_twitch.replace("{lenght}",    str(display_map.lenght))
		chat_response_twitch = chat_response_twitch.replace("{bpm}",       str(display_map.bpm))
		chat_response_twitch = chat_response_twitch.replace("{creator}",   str(display_map.creator))
		chat_response_twitch = chat_response_twitch.replace("{requester}", str(message.display_name))
		chat_response_twitch = chat_response_twitch.replace("{osu_link}",  str(odf))

		#prepare message and give to right loop
		res_o = BASE.osu.send_pm(osu_user, chat_response_osu)
		asyncio.ensure_future(res_o,loop=BASE.Osu_loop)

		return await BASE.twitch.send_message(message.channel_name, chat_response_twitch)
