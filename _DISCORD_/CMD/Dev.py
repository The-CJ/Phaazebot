#BASE.moduls._Discord_.CMD.Dev

from imp import reload
import asyncio, discord, traceback, math, sys, threading, random, json

async def base(BASE, message):
	m = message.content.split(" ")
	check = m[0][5:]

	if check=="-!-":
		await BASE.convert_DB(BASE)

	if check.startswith("debug"):

		if check.startswith("debug+++"):
			return await BASE.phaaze.send_message(message.channel, "Unknown Overwrite Command.")

		elif check.startswith("debug++"):
			await super_debug(BASE, message)

		elif check.startswith("debug+"):
			if len(m) == 1: return

			command = " ".join(m for m in m[1:])
			command = command.strip("`")
			await debug_async(BASE, message, command)

		else:
			if len(m) == 1: return

			command = " ".join(m for m in m[1:])
			command = command.strip("`")
			await debug(BASE, message, command)

	elif check.startswith("reload"):
		await BASE.phaaze.send_message(message.channel, ":warning: Reloading entire PhaazeOS Infobase... :recycle:")
		try:
			await BASE.moduls.Utils.reload_(BASE)
			await BASE.phaaze.send_message(message.channel, ":white_check_mark: Reload successfull.")
		except:
			return await BASE.phaaze.send_message(message.channel, ":octagonal_sign: Database is corrupted! Keeping old Database alive.")

	elif check.startswith("global"):
		await global_shit(BASE, message)

	elif check.startswith("news"):
		await news_shit(BASE, message)

	elif check.startswith("shutdown"):
		try: await BASE.phaaze.send_message(message.channel, "PhaazeOS will now shutdown savely.")
		except: pass

		await BASE.shutdown(BASE)

	else:
		return await BASE.phaaze.send_message(message.channel, "Unknown Overwrite Command.")

async def debug(BASE, message, command):
	try:
		f = eval(command)
		g = discord.Embed(name="Debug",description=str(f))
		await BASE.phaaze.send_message(message.channel, embed=g)
	except Exception as Fail:
		await BASE.phaaze.send_message(message.channel, "ERROR:\n\n```"+str(Fail)+"```")

async def debug_async(BASE, message, command):
	try:
		f = await eval(command)
		g = discord.Embed(name="Debug",description=str(f))
		await BASE.phaaze.send_message(message.channel, embed=g)
	except Exception as Fail:
		await BASE.phaaze.send_message(message.channel, "ERROR:\n\n```"+str(Fail)+"```")

async def super_debug(BASE, message):
	command, code = message.content.split(" ", 1)
	code = code.replace("```py", "")
	code = code.strip("`")

	debug_file = open("STUFF/super_debug.py", "wb")
	debug_file.write(bytes(code, "UTF-8"))
	debug_file.close()

	try:
		import STUFF.super_debug as SDB
		SDB = reload(SDB)
	except Exception as Fail:
		return await BASE.phaaze.send_message(message.channel, "Error in Modul importing:\n\n```"+str(Fail)+"```")

	try:
		await SDB.debug(BASE, message)
		return await BASE.phaaze.send_message(message.channel, "Successful debuged")

	except Exception as Fail:
		return await BASE.phaaze.send_message(message.channel, "Error inside Debug:\n\n```"+str(Fail)+"```\n\nor missing start function. Phaaze will call a ```py\nasync def debug(BASE, message): ...``` inside the modul")

async def global_shit(BASE, message):
	mes = open("UTILS/global_message.txt", "r").read()

	l = "Wanna send: ```{0}``` to every server?\n\n'y' >>> "

	await BASE.phaaze.send_message(message.channel, l.format(mes))

	u = await BASE.phaaze.wait_for_message(timeout=30, author=message.author, channel=message.channel)

	if u.content == "y":
		for server in BASE.phaaze.servers:
			try:
				await BASE.phaaze.send_message(server, mes)
			except:
				pass

		return await BASE.phaaze.send_message(message.channel, "Finished.")
	else:
		return await BASE.phaaze.send_message(message.channel, ":warning: Canceled!")

async def news_shit(BASE, message):
	mes = open("UTILS/global_news_message.txt", "r").read()

	channels = open("UTILS/server_channel_id_for_news.json", "r").read()
	channels = json.loads(channels)

	all_channels = channels.get("news_channels", [])

	l = "Wanna send: ```{0}``` to {1} news active channels?\n\n'y' >>> ".format(mes, str(len(all_channels)))

	await BASE.phaaze.send_message(message.channel, l)

	u = await BASE.phaaze.wait_for_message(timeout=30, author=message.author, channel=message.channel)

	if u.content == "y":
		await BASE.moduls._Twitter_.Base.send_tweet(BASE, mes)
		for channel_id in all_channels:
			try:
				await BASE.phaaze.send_message(discord.Object(id=channel_id), mes)
			except:
				pass

		return await BASE.phaaze.send_message(message.channel, "Finished.")

	else:
		return await BASE.phaaze.send_message(message.channel, ":warning: Canceled!")
