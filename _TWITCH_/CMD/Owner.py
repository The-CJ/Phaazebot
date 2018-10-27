#BASE.modules._Twitch_.CMD.Owner

import asyncio

async def Base(BASE, message, **kwargs):
	m = message.content[len(BASE.vars.TRIGGER_TWITCH):].lower().split(" ")
	check = m[0]

	# # #
	return


