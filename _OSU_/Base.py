#BASE.moduls._Osu_.Base

import asyncio

async def on_message(BASE, message):
	if message.content.lower().startswith("!verify"):
		await BASE.moduls._Osu_.Utils.verify(BASE, message)

	elif message.content.startswith("ACTION is listening to"):
		await np_response(BASE, message)

	elif message.content.lower().startswith("!disconnect"):
		await BASE.moduls._Twitch_.Utils.delete_verify(BASE, message.name, platform="osu")
		await BASE.Osu_IRC.send_message(message.name, "Disconnected!")

async def np_response(BASE, message):
	x = message.content.split("[")[1]
	link = x.split(" ")[0]
	_id = link.split("/b/")[1]

	r = await BASE.moduls.osu_utils.get_pp(_id)
	response = "This with: FC - 100% would give: {0}pp (+-2%)".format(str(round(r.pp,1)))
	await BASE.Osu_IRC.send_message(message.name, response)
