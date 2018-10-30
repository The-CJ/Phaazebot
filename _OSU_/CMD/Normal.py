# BASE.modules._Osu_.CMD.Normal

import asyncio

async def Base(BASE, message):

	m = message.content[len(BASE.vars.TRIGGER_OSU):].lower().split(" ")
	check = m[0]

	if check.startswith("twitchverify"):
		return await BASE.modules._Osu_.PROCESS.Normal.TwitchVerify.Base(BASE, message)

