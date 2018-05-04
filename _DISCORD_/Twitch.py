#BASE.moduls._Discord_.Twitch

import asyncio, discord

async def Base(BASE, message, kwargs):
	AV = ["track", "get", "reset"]
	m = message.content.split(" ")

	if len(m) == 1:
		return await BASE.discord.send_message(
			message.channel,
			":warning: You need to add a option, available are: {0}".format(" ".join(f"`{g}`" for g in AV)))

	if m[1].lower() == "track":
		if len(m) <= 2:
			return await BASE.discord.send_message(message.channel, ":warning: You need to add a Twitch channel name to enable/disable alerts")

		return await track(BASE, message, kwargs, m[2])

	elif m[1].lower() == "custom" and ""=="-":
		await BASE.discord.send_message(message.channel, ":no_entry_sign: SOON:tm: or so")

	elif m[1].lower() == "get":
		return await get(BASE, message, kwargs)

	elif m[1].lower() == "reset":
		return await reset(BASE, message, kwargs)

	else:
		return await BASE.discord.send_message(message.channel, ":warning: `{1}` is not a option, available are: {0}".format(" ".join(f"`{g}`" for g in AV), m[1]))

async def track(BASE, message, kwargs, twitch_name):

	#get channel + check if a real channel
	chan = BASE.moduls._Twitch_.Utils.get_user(BASE, twitch_name, search="name")
	if chan == None:
		return await BASE.discord.send_message(
			message.channel,
			f":warning: There is no channel called: `{twitch_name}`\nOr Twitch API is down. Make sure you don't make a typo and try again.")

	chan = chan[0]

	state = BASE.moduls._Twitch_.Alerts.Main.Discord.toggle_chan(BASE, chan.get("_id", None), message.channel.id)

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
	res = BASE.PhaazeDB.select(
		of=f"twitch/alerts",
		where=f"'{message.channel.id}' in data['discord_channel']"
	)

	if not res.get('data', []):
		return await BASE.discord.send_message(message.channel, f":information_source: No Twitch channels are tracked in {message.channel.mention}")

	channel = [a.get('twitch_id', "0") for a in res.get('data', [])]

	channel_result = BASE.moduls._Twitch_.Utils.get_user(BASE, channel, search="id")

	if channel_result == None:
		return await BASE.discord.send_message(message.channel, f":information_source: No valid Twitch channels are tracked in {message.channel.mention}")

	x = ",".join( f"`{x.get('display_name', 'N/A')}`" for x in channel_result )
	return await BASE.discord.send_message(message.channel, f":information_source:  All tracked Twitch channel in {message.channel.mention}\n\n{x}")

async def reset(BASE, message, kwargs):
	res = BASE.PhaazeDB.select(
		of=f"twitch/alerts",
		where=f"'{message.channel.id}' in data['discord_channel']"
	)

	res = res.get('data', [])

	for match in res:
		twitch_id = match.get('twitch_id', None)
		match['discord_channel'].remove(message.channel.id)

		BASE.PhaazeDB.update(
			of = f"twitch/alerts",
			where = f"data['twitch_id'] == '{twitch_id}'",
			content = dict (discord_channel = match['discord_channel'])
		)


	return await BASE.discord.send_message(message.channel, f":white_check_mark: All tracked Twitch channel in {message.channel.mention}\nHave been removed")

