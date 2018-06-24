#BASE.modules._TWITCH_.CMD.Normal

import asyncio

async def Base(BASE, message, **kwargs):
	m = message.content.lower().split(" ")
	check = m[0][1:]

async def Main_channel(BASE, message, **kwargs):
	m = message.content.lower().split(" ")
	check = m[0][1:]

	#redirect to PROCCESS.Owner
	if check.startswith("join"):
		return await BASE.modules._Twitch_.PROCESS.Owner.Everything.join(BASE, message, kwargs)

	if check.startswith("leave"):
		return await BASE.modules._Twitch_.PROCESS.Owner.Everything.leave(BASE, message, kwargs)

