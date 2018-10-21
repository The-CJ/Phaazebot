#BASE.modules._Twitch_.CMD.Owner

import asyncio

async def Base(BASE, message, **kwargs):
	m = message.content.lower().split(" ")
	check = m[0][1:]

	# # #
	return

	if check.startswith("master"):
		return await BASE.modules._Discord_.PROCESS.Owner.Master.Base(BASE, message, kwargs)

	if check.startswith("welcome"):
		return await BASE.modules._Discord_.PROCESS.Owner.Welcome.Base(BASE, message, kwargs)

	if check.startswith("leave"):
		return await BASE.modules._Discord_.PROCESS.Owner.Leave.Base(BASE, message, kwargs)

	if check.startswith("autorole"):
		return await BASE.modules._Discord_.PROCESS.Owner.Autorole.Base(BASE, message, kwargs)

	if check.startswith("logs"):
		return await BASE.modules._Discord_.PROCESS.Owner.Logs.Base(BASE, message, kwargs)

	if check.startswith("news"):
		return await BASE.modules._Discord_.PROCESS.Owner.Everything.news(BASE, message, kwargs) #TODO: Fix

	if check.startswith("twitch"):
		return await BASE.modules._Discord_.Twitch.Base(BASE, message, kwargs)


