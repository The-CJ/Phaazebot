#BASE.moduls._Discord_.PROCESS.Dev

import asyncio, discord, json

async def debug(BASE, message, kwargs):
	m = message.content.split(" ", 2).pop()

	try:
		f = eval(m)
		await BASE.discord.send_message(message.channel, f)
	except Exception as Fail:
		await BASE.discord.send_message(message.channel, "ERROR:\n\n```"+str(Fail)+"```")

async def global_message(BASE, message, kwargs):
	mes = open("UTILS/global_message.txt", "r").read()

	l = f"Wanna send: ```{mes}``` to all servers?\n\n'y' >>> "

	await BASE.discord.send_message(message.channel, l)

	u = await BASE.discord.wait_for_message(timeout=30, author=message.author, channel=message.channel)

	if u.content == "y":
		for server in BASE.discord.servers:
			try:
				await BASE.discord.send_message(server, mes)
			except:
				pass

		return await BASE.discord.send_message(message.channel, "Finished.")
	else:
		return await BASE.discord.send_message(message.channel, ":warning: Canceled!")

async def news(BASE, message, kwargs):
	mes = open("UTILS/global_news_message.txt", "r").read()

	channels = open("UTILS/server_channel_id_for_news.json", "r").read()
	channels = json.loads(channels)

	all_channels = channels.get("news_channels", [])

	l = "Wanna send: ```{0}``` to {1} news active channels?\n\n'y' >>> ".format(mes, str(len(all_channels)))

	await BASE.discord.send_message(message.channel, l)

	u = await BASE.discord.wait_for_message(timeout=30, author=message.author, channel=message.channel)

	if u.content == "y":
		await BASE.moduls._Twitter_.Base.send_tweet(BASE, mes)
		for channel_id in all_channels:
			try:
				await BASE.discord.send_message(discord.Object(id=channel_id), mes)
			except:
				pass

		return await BASE.discord.send_message(message.channel, "Finished.")

	else:
		return await BASE.discord.send_message(message.channel, ":warning: Canceled!")
