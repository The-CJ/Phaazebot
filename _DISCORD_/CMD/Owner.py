#BASE.moduls._Discord_.CMD.Owner

import asyncio, json
Available = ["mod_levels", "disable_levels"]

async def base(BASE, message):

	m = message.content.lower().split(" ")
	check = m[0][3:]

	if check.startswith("master"):
		if await BASE.moduls.Utils.is_Owner(BASE, message):
			await BASE.moduls.Owner_Commands.master(BASE, message)
		else:
			await BASE.moduls.Utils.no_owner(BASE, message)

	if check.startswith("welcome"):
		if await BASE.moduls.Utils.is_Owner(BASE, message):
			await BASE.moduls.Owner_Commands.welcome.welcome(BASE, message)
		else:
			await BASE.moduls.Utils.no_owner(BASE, message)

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
