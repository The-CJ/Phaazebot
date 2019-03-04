#BASE.molinked_osu_accountdules._TWITCH_.CMD.Normal

import asyncio

async def Base(BASE, message, **kwargs):
	m = message.content[len(BASE.vars.TRIGGER_TWITCH):].lower().split(" ")
	check = m[0]

	if check.startswith("stats"):
		return await BASE.modules._Twitch_.Level.stats(BASE, message, kwargs)

	if check.startswith("leaderboard"):
		return await BASE.modules._Twitch_.Level.leaderboard(BASE, message, kwargs)

	if check.startswith("quote"):
		return await BASE.modules._Twitch_.PROCESS.Normal.Quote.Base(BASE, message, kwargs)

	if check.startswith("battle"):
		return await BASE.modules._Twitch_.Games.Battle.Base(BASE, message, kwargs)

	if check.startswith("mission"):
		return await BASE.modules._Twitch_.Games.Mission.Base(BASE, message, kwargs)

#only get called when the channel name = the bots nickname
async def Main_channel(BASE, message, **kwargs):
	m = message.content[len(BASE.vars.TRIGGER_TWITCH):].lower().split(" ")
	check = m[0]

	#redirect to PROCCESS.Owner
	if check.startswith("join"):
		return await BASE.modules._Twitch_.PROCESS.Owner.Everything.join(BASE, message, kwargs)

	if check.startswith("leave"):
		return await BASE.modules._Twitch_.PROCESS.Owner.Everything.leave(BASE, message, kwargs)

