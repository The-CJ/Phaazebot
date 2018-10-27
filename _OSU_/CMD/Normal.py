# BASE.modules._Osu_.CMD.Normal

import asyncio

async def Base(BASE, message):

	m = message.content[BASE.vars.TRIGGER_OSU].lower().split(" ")
	check = m[0]

