#BASE.modules._Twitch_.PROCESS.Mod

import asyncio

class Quote(object):

	async def add(BASE, message, kwargs):
		m = message.content[len(BASE.vars.TRIGGER_TWITCH):].split(" ")

		if len(m) <= 1:
			r = f"Error! > {BASE.vars.TRIGGER_TWITCH}addquote [Content]"
			return await BASE.twitch.send_message(message.channel_name, r)

		channel_quotes = await BASE.modules._Twitch_.Utils.get_channel_quotes(BASE, message.channel_id)

		if len(channel_quotes) >= BASE.limit.TWITCH_QUOTE_AMOUNT:
			return await BASE.twitch.send_message(message.channel_name, f"Error: There are already {BASE.limit.TWITCH_QUOTE_AMOUNT} quotes, delete some first")

		quote_content = " ".join(m[1:])

		ins = BASE.PhaazeDB.insert(into=f"twitch/quotes/quotes_{message.channel_id}", content=dict(content=quote_content))

		_id_ = ins.get('data', {}).get('id', '[N/A]')

		return await BASE.twitch.send_message(message.channel_name, f'Quote successfull added, ID: "{str(_id_)}"')

	async def rem(BASE, message, kwargs):
		m = message.content[len(BASE.vars.TRIGGER_TWITCH):].split(" ")

		if len(m) <= 1:
			r = f"Error! > {BASE.vars.TRIGGER_TWITCH}delquote [ID]"
			return await BASE.twitch.send_message(message.channel_name, r)

		_id_ = m[1] if m[1].isdigit() else None

		if _id_ == None:
			return await BASE.twitch.send_message(message.channel_name, f'"{str(_id_)}" is not a valid quote id')

		dele = BASE.PhaazeDB.delete(of=f"twitch/quotes/quotes_{message.channel_id}", where=f"str(data['id']) == str('{str(_id_)}')")
		h = dele.get('hits', 0)
		if h == 1:
			return await BASE.twitch.send_message(message.channel_name, f'Quote "{str(_id_)}" successfull deleted')
		else:
			return await BASE.twitch.send_message(message.channel_name, f' There is not quote with index "{str(_id_)}"')

class Settings(object):
	AVAILABLE = dict(
		custom = "active_custom",
		level = "active_level",
		quote = "active_quotes",
		game = "active_games"
	)

	async def Base(BASE, message, kwargs):
		m = message.content[len(BASE.vars.TRIGGER_TWITCH):].lower().split()

		if len(m) == 1:
			return await BASE.twitch.send_message(message.channel_name, f'@{message.display_name}, Missing option! Available are: {", ".join(Settings.AVAILABLE)}')

		if m[1] not in Settings.AVAILABLE:
			return await BASE.twitch.send_message(message.channel_name, f'@{message.display_name}, "{m[1]}" is not option! Available are: {", ".join(Settings.AVAILABLE)}')

		return await Settings.change_option(BASE, message, m[1] ,kwargs)

	async def change_option(BASE, message, field, kwargs):
		m = message.content[len(BASE.vars.TRIGGER_TWITCH):].lower().split()


		if len(m) == 2:
			return await BASE.twitch.send_message(message.channel_name, f'@{message.display_name}, "{m[0]} {m[1]}" is missing a valid state, try: "on"/"off"')

		state = Settings.get_state(m[2])

		if state == None:
			return await BASE.twitch.send_message(message.channel_name, f'@{message.display_name}, "{m[2]}" is a invalid state, try: "on"/"off"')

		channel_settings = kwargs.get('channel_settings', None)
		if channel_settings == None:
			channel_settings = await BASE.modules._Twitch_.Utils.get_channel_settings(BASE, message.channel_id)

		db_field = Settings.AVAILABLE.get(field, None)
		if db_field == None: raise AttributeError("Invalid db_field search: "+field)

		current_state = channel_settings.get(db_field, False)

		if current_state and state:
			return await BASE.twitch.send_message(message.channel_name, f'@{message.display_name}, setting: "{m[1]}" is already active!')

		if not current_state and not state:
			return await BASE.twitch.send_message(message.channel_name, f'@{message.display_name}, setting: "{m[1]}" was not active')

		BASE.PhaazeDB.update(
			of = "twitch/channel_settings",
			where = f"data['channel_id'] == '{message.channel_id}'",
			content = f"data['{db_field}'] = {str(state)}"
		)
		state = "disabled" if not state else "enabled"
		return await BASE.twitch.send_message(message.channel_name, f'@{message.display_name}, setting: "{m[1]}" is now {state}')

	def get_state(value):
		value = value.lower()
		if value in [True, 'on', 'enable', 'yes']:
			return True

		elif value in [False, 'off', 'disable', 'no']:
			return False

		else: return None
