#BASE.modules._Discord_.Twitch

import asyncio, discord

async def Base(BASE, message, kwargs):
	AV = ["track", "get", "clear", "custom"]
	m = message.content[(len(BASE.vars.TRIGGER_DISCORD)*3):].split(" ")

	if len(m) == 1:
		return await BASE.discord.send_message(
			message.channel,
			":warning: You need to add a option, available are: {0}".format(" ".join(f"`{g}`" for g in AV)))

	if m[1].lower() == "track":
		if len(m) <= 2:
			return await BASE.discord.send_message(message.channel, ":warning: You need to add a Twitch channel name to enable/disable alerts")

		return await track(BASE, message, kwargs, " ".join(m[2:]))

	elif m[1].lower() == "custom":
		if len(m) <= 2:
			return await BASE.discord.send_message(message.channel, f":warning: You need to add a custom format to the alert:\n`{BASE.vars.TRIGGER_DISCORD*3}twitch custom [Custom_message]`")

		return await custom(BASE, message, kwargs, " ".join(m[2:]))

	elif m[1].lower() == "get":
		return await get(BASE, message, kwargs)

	elif m[1].lower() == "clear":
		return await clear(BASE, message, kwargs)

	else:
		return await BASE.discord.send_message(message.channel, ":warning: `{1}` is not a option, available are: {0}".format(" ".join(f"`{g}`" for g in AV), m[1]))

async def track(BASE, message, kwargs, twitch_name):

	#get channel + check if a real channel
	chan = BASE.modules._Twitch_.Utils.get_user(BASE, twitch_name, search="name")
	if chan == None:
		return await BASE.discord.send_message(
			message.channel,
			f":warning: There is no channel called: `{twitch_name}`\nOr Twitch API is down. Make sure you don't make a typo and try again.")

	chan = chan[0]

	state = BASE.modules._Twitch_.Streams.Main.Discord.toggle_chan(BASE, chan.get("id", None), message.channel.id, twitch_name=chan.get('login', None))

	display_name = chan.get('display_name',"N/A")
	if state == "add":
		return await BASE.discord.send_message(
			message.channel,
			f":white_check_mark: **{display_name}** is now tracked in {message.channel.mention} :large_blue_circle:")
	elif state == "remove":
		return await BASE.discord.send_message(
			message.channel,
			f":white_check_mark: **{display_name}** will no longer be tracked in {message.channel.mention} :red_circle:")
	else:
		return await BASE.discord.send_message(
			message.channel,
			f":warning: Something Strange happen, your changes could not be processed, maybe Twitch Alerts are disbled by the Developer?")

async def get(BASE, message, kwargs):
	tracked_channel = BASE.modules._Twitch_.Streams.Main.Discord.get_alerts_for_channel(BASE, message.channel.id)

	if not tracked_channel:
		return await BASE.discord.send_message(message.channel, f":information_source: No Twitch channels are tracked in {message.channel.mention}")

	x = ",".join( f"`{x.get('twitch_name', 'N/A')}`" for x in tracked_channel )
	return await BASE.discord.send_message(message.channel, f":information_source: All tracked Twitch channel in {message.channel.mention}\n\n{x}")

async def clear(BASE, message, kwargs):
	removed_alerts = BASE.modules._Twitch_.Streams.Main.Discord.clear_channel_alerts(BASE, message.channel.id)

	if not removed_alerts:
		return await BASE.discord.send_message(message.channel, f":information_source: {message.channel.mention} don't have any alerts")

	x = " ".join( f"`{c.get('twitch_name', '-')}`" for c in removed_alerts)

	return await BASE.discord.send_message(
		message.channel,
		f":white_check_mark: All tracked Twitch channel in {message.channel.mention} have been removed\n\nRemoved Tracked channels: {x}")

async def custom(BASE, message, kwargs, custom_alert):
	if custom_alert.lower() == "clear":
		BASE.PhaazeDB.delete(of='twitch/alert_format', where=f"data['discord_channel_id'] == '{message.channel.id}'")
		return await BASE.discord.send_message(message.channel, ':white_check_mark: Custom alert cleared')


	res = BASE.PhaazeDB.select(of=f"twitch/alert_format", where=f"data['discord_channel_id'] == '{message.channel.id}'", limit=1)
	found = True if res.get('data', []) else False

	if custom_alert.lower() == "get":
		if found:
			e = res.get('data', [])[0]
			a = e.get('custom_alert', "[N/A]")
			return await BASE.discord.send_message(message.channel, f':white_check_mark: Current Custom alert:\n```{a}```')
		else:
			return await BASE.discord.send_message(message.channel, f':warning: This channel has no custom alert')

	else:
		if found:
			BASE.PhaazeDB.update(of="twitch/alert_format", content=dict(custom_alert=custom_alert), where=f"data['discord_channel_id'] == '{message.channel.id}'", limit=1)
			return await BASE.discord.send_message(message.channel, ':white_check_mark: Custom alert updated')
		else:
			BASE.PhaazeDB.insert(into="twitch/alert_format", content=dict(custom_alert=custom_alert, discord_channel_id=message.channel.id))
			return await BASE.discord.send_message(message.channel, ':white_check_mark: Custom alert set')

