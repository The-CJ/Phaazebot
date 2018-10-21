#BASE.modules._Osu_.Base

import asyncio

async def on_message(BASE, message):

	# i don't think i should phaaze listen to channels, so for now i only handle privmsg
	# NOTE: in theory i never join a channel, just to be sure
	if message.type == "channel": return

	if message.content.startswith("!"):
		await BASE.modules._Osu_.CMD.Normal.Base(BASE, message)

