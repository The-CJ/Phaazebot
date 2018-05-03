#BASE.moduls._Discord_.CMD.Dev

import asyncio, discord, traceback, math, sys, threading, random, json

async def Base(BASE, message, **kwargs):
	m = message.content.split(" ")
	check = m[0][5:]

	if check.startswith("debug"):
		await BASE.moduls._Discord_.PROCESS.Dev.debug(BASE, message, kwargs)

	elif check.startswith("reload"):
		await BASE.discord.send_message(message.channel, ":warning: Reloading entire PhaazeOS. Please wait.")
		asyncio.ensure_future(BASE.moduls.Utils.reload_base(BASE), loop=BASE.Worker_loop)

	elif check.startswith("global"):
		await BASE.moduls._Discord_.PROCESS.Dev.global_message(BASE, message, kwargs)

	elif check.startswith("news"):
		await BASE.moduls._Discord_.PROCESS.Dev.news(BASE, message, kwargs)

	elif check.startswith("shutdown"):
		try: await BASE.discord.send_message(message.channel, "PhaazeOS will now shutdown savely.")
		except: pass

		await BASE.shutdown(BASE)

	else:
		return await BASE.discord.send_message(message.channel, "Unknown Overwrite Command.")
