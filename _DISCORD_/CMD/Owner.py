#BASE.moduls._Discord_.CMD.Owner

import asyncio, json

async def Base(BASE, message, **kwargs):
	if not await BASE.moduls._Discord_.Utils.is_Owner(BASE, message):
		async def no_owner(BASE, message, kwargs):
			m = await BASE.phaaze.send_message(message.channel, ":no_entry_sign: You can not use Owner Commands")
			await asyncio.sleep(2.5)
			await BASE.phaaze.delete_message(m)

		asyncio.ensure_future(no_owner(BASE, message, kwargs))
		return

	m = message.content.lower().split(" ")
	check = m[0][3:]

	if check.startswith("master"):
		return await BASE.moduls._Discord_.PROCESS.Owner.master.Base(BASE, message, kwargs)

	if check.startswith("welcome"):
		return await BASE.moduls._Discord_.PROCESS.Owner.welcome.Base(BASE, message, kwargs)

	return

	if check.startswith("leave"):
		if await BASE.moduls.Utils.is_Owner(BASE, message):
			await BASE.moduls.Owner_Commands.leave.leave(BASE, message)
		else:
			await BASE.moduls.Utils.no_owner(BASE, message)

	if check.startswith("logs"):
		if await BASE.moduls.Utils.is_Owner(BASE, message):
			await BASE.moduls.Owner_Commands.logs.logs_base(BASE, message)
		else:
			await BASE.moduls.Utils.no_owner(BASE, message)

	if check.startswith("twitch"):
		if await BASE.moduls.Utils.is_Owner(BASE, message):
			await BASE.moduls.Twitch.twitch_alerts_base(BASE, message)
		else:
			await BASE.moduls.Utils.no_owner(BASE, message)

	if check.startswith("autorole"):
		if await BASE.moduls.Utils.is_Owner(BASE, message):
			await BASE.moduls.Owner_Commands.autorole.base(BASE, message)
		else:
			await BASE.moduls.Utils.no_owner(BASE, message)

	if check.startswith("news"):
		if await BASE.moduls.Utils.is_Owner(BASE, message):
			await BASE.moduls.Owner_Commands.news(BASE, message)
		else:
			await BASE.moduls.Utils.no_owner(BASE, message)
