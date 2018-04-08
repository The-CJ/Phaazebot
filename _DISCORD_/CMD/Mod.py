#BASE.moduls._Discord_.CMD.Mod

import asyncio

async def no_mod(BASE, message, kwargs):
	m = await BASE.phaaze.send_message(message.channel, ":no_entry_sign: You can not use Mod Commands")
	await asyncio.sleep(2.5)
	await BASE.phaaze.delete_message(m)

async def owner_disabled_mod(BASE, message, kwargs):
	m = await BASE.phaaze.send_message(message.channel, ":no_entry_sign: The Serverowner disabled Mod-commands, only the Serverowner can use them")
	await asyncio.sleep(2.5)
	await BASE.phaaze.delete_message(m)

async def Base(BASE, message, **kwargs):
	if not await BASE.moduls._Discord_.Utils.is_Mod(BASE, message):
		asyncio.ensure_future(no_mod(BASE, message, kwargs))
		return

	if not await BASE.moduls._Discord_.Utils.is_Owner(BASE, message) and kwargs.get('server_setting', {}).get('owner_disable_mod', False):
		asyncio.ensure_future(owner_disabled_mod(BASE, message, kwargs))
		return

	m = message.content.lower().split(" ")
	check = m[0][2:]

	if check.startswith("setting"):
		return await BASE.moduls._Discord_.PROCESS.Mod.Settings.Base(BASE, message, kwargs)

	if check.startswith("addcom"):
		return await BASE.moduls._Discord_.Custom.add(BASE, message, kwargs)

	if check.startswith("delcom"):
		return await BASE.moduls._Discord_.Custom.rem(BASE, message, kwargs)

	if check.startswith("blacklist"):
		return await BASE.moduls._Discord_.Blacklist.Base(BASE, message, kwargs)

	if check.startswith("quote"):
		return await BASE.moduls._Discord_.PROCESS.Mod.Quote.Base(BASE, message, kwargs)

	if check.startswith("prune"):
		return await BASE.moduls._Discord_.PROCESS.Mod.Prune.Base(BASE, message, kwargs)

	return

	if check.startswith("serverinfo"):
		if await BASE.moduls.Utils.is_Mod(BASE, message):
			await BASE.moduls.Mod_Commands.serverinfo(BASE, message)
		else:
			await BASE.moduls.Utils.no_mod(BASE, message)

	if check.startswith("getrole"):
		if await BASE.moduls.Utils.is_Mod(BASE, message):
			await BASE.moduls.Mod_Commands.get_roles(BASE, message)
		else:
			await BASE.moduls.Utils.no_mod(BASE, message)

	if check.startswith("level"):
		if await BASE.moduls.Utils.is_Mod(BASE, message):
			await BASE.moduls.Mod_Commands.level_base(BASE, message)
		else:
			await BASE.moduls.Utils.no_mod(BASE, message)
