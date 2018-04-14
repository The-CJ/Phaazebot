#BASE.moduls._Discord_.CMD.Owner

import asyncio

CMDs = ['master', 'welcome', 'leave', 'autorole', 'logs', 'news', 'twitch']

async def no_owner(BASE, message, kwargs):
	m = await BASE.phaaze.send_message(message.channel, ":no_entry_sign: You can not use Owner Commands")
	await asyncio.sleep(2.5)
	await BASE.phaaze.delete_message(m)

async def Base(BASE, message, **kwargs):
	m = message.content.lower().split(" ")
	check = m[0][3:]

	if not await BASE.moduls._Discord_.Utils.is_Owner(BASE, message):
		if any([True if check.startswith(cmd) else False for cmd in CMDs]):
			asyncio.ensure_future(no_owner(BASE, message, kwargs))
			return

	# # #

	if check.startswith("master"):
		return await BASE.moduls._Discord_.PROCESS.Owner.Master.Base(BASE, message, kwargs)

	if check.startswith("welcome"):
		return await BASE.moduls._Discord_.PROCESS.Owner.Welcome.Base(BASE, message, kwargs)

	if check.startswith("leave"):
		return await BASE.moduls._Discord_.PROCESS.Owner.Leave.Base(BASE, message, kwargs)

	if check.startswith("autorole"):
		return await BASE.moduls._Discord_.PROCESS.Owner.Autorole.Base(BASE, message, kwargs)

	if check.startswith("logs"):
		return await BASE.phaaze.send_message(
			message.channel,
			f":grey_exclamation: PhaazeDiscord-Logs configuration has moved to the PhaazeWebsite\n"\
			f"		Goto https://phaaze.net/discord/dashboard/{message.server.id}#logs and log-in to configure everything"
			)

	if check.startswith("news"):
		return await BASE.moduls._Discord_.PROCESS.Owner.Everything.news(BASE, message, kwargs)

	return

	if check.startswith("twitch"):
		if await BASE.moduls.Utils.is_Owner(BASE, message):
			await BASE.moduls.Twitch.twitch_alerts_base(BASE, message)
		else:
			await BASE.moduls.Utils.no_owner(BASE, message)


