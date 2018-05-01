#BASE.moduls._Discord_.Twitch

import asyncio, discord

async def Base(BASE, message, kwargs):
	AV = ["track", "custom", "get", "reset"]
	m = message.content.split(" ")

	if len(m) == 1:
		return await BASE.phaaze.send_message(
			message.channel,
			":warning: You need to add a option, available are: {0}".format(" ".join(f"`{g}`" for g in AV)))

	if m[1].lower() == "track":
		if len(m) <= 2:
			return await BASE.phaaze.send_message(message.channel, ":warning: You need to add a Twitch channel name to enable/disable alerts")

		return await track(BASE, message, kwargs, m[2])

	elif m[1].lower() == "custom":
		if len(m) == 2:
			await BASE.phaaze.send_message(message.channel, ":warning: missing option: `message`, `game` or `template`")
		elif m[2].lower() == "message":
			await change_custom_settings(BASE, message, "message")
		elif m[2].lower() == "game":
			await change_custom_settings(BASE, message, "game")
		elif m[2].lower() == "template":
			await change_custom_settings(BASE, message, "template")
		else:
			await BASE.phaaze.send_message(message.channel, ":warning: `{0}` is not a option, try: `message`, `game` or `template`".format(m[2].lower()))

	elif m[1].lower() == "get":
		found = []
		for file in os.listdir("UTILS/twitch_streams"):
			if file.endswith(".json") and not file.startswith("_"):
				with open("UTILS/twitch_streams/"+file, "r") as stream_file:
					stream_file = json.loads(stream_file.read())
					if message.channel.id in stream_file["d_channel"]:
						found.append(file.replace(".json", ""))

		response = await twitch_API_call(BASE, "https://api.twitch.tv/kraken/users?id=" + ",".join(_id for _id in found))

		if response.get("stats", 200) == 400:
			return await BASE.phaaze.send_message(message.channel, ":information_source: No active Twitch Alerts in {0}".format(message.channel.mention))

		if response.get("_total", 0) == 0:
			return await BASE.phaaze.send_message(message.channel, ":information_source: No active Twitch Alerts in {0}".format(message.channel.mention))

		found_names = [stream["display_name"] for stream in response["users"]]

		e = ", ".join(name for name in found_names)
		return await BASE.phaaze.send_message(message.channel, ":information_source: Twitch Alerts in {0} for Twitch Channels: {1}".format(message.channel.mention, e))

	elif m[1].lower() == "reset":
		pass

	else:
		return await BASE.phaaze.send_message(message.channel, ":warning: `{1}` is not a option, available are: {0}".format(" ".join(f"`{g}`" for g in AV), m[1]))

async def track(BASE, message, kwargs, twitch_name):

	#get channel + check if a real channel
	chan = BASE.moduls._Twitch_.Utils.get_user(BASE, twitch_name, search="name")
	if chan == None:
		return await BASE.phaaze.send_message(
			message.channel,
			f":warning: There is no channel called: `{twitch_name}`\nOr Twitch API is down. Make sure you don't make a typo and try again.")

	state = BASE.moduls._Twitch_.Alerts.Main.Discord.toggle_chan(BASE, chan.get("_id", None), message.channel.id)

	display_name = chan.get('display_name',"N/A")
	if state == "add":
		return await BASE.phaaze.send_message(
			message.channel,
			f":white_check_mark: **{display_name}** is now tracked in {message.channel.mention} :large_blue_circle:")
	elif state == "remove":
		return await BASE.phaaze.send_message(
			message.channel,
			f":white_check_mark: **{display_name}** will no longer be tracked in {message.channel.mention} :red_circle:")
	else:
		return await BASE.phaaze.send_message(
			message.channel,
			f":warning: Something Strange happen, your changes could not be processed, maybe Twitch Alerts are disbled by the Developer?")
