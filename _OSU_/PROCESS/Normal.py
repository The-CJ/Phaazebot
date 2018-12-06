# BASE.modules._Osu_.PROCESS.Mod

import asyncio

class TwitchVerify(object):

	async def Base(BASE, message):
		m = message.content[len(BASE.vars.TRIGGER_OSU):].split(" ")

		if len(m) <= 1:
			return await BASE.osu.send_pm(message.name, f"To link a twitch channel with your osu! account, please type '{BASE.vars.TRIGGER_TWITCH}osulink {message.name}' in your twitch channel and follow the instructions")

		code = m[1] #should be non space

		Pair = None

		All_PO = BASE.modules._Twitch_.PROCESS.Owner.OsuLink.in_linking_process
		for Pair_O in All_PO:
			if Pair_O.pairing_code == code:
				Pair = Pair_O
				break

		if Pair == None:
			return await BASE.osu.send_pm(
				message.name,
				f"The code you provided does not match any avaliable twitch-pair-links"
			)

		if Pair.osu_name.lower() == message.name.lower():
			Pair.activate()
		else:
			return await BASE.osu.send_pm(
				message.name,
				"The code is maybe right... but your name issn't the right one, if it is, please contact 'The_CJ' and report a bug"
			)

		# we don't need a return message, since that should do the pair object
