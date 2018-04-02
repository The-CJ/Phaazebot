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

	if not BASE.moduls._Discord_.Utils.is_Owner(BASE, message) and kwargs.get('server_setting', {}).get('owner_disable_mod', False):
		asyncio.ensure_future(owner_disabled_mod(BASE, message, kwargs))
		return

	m = message.content.lower().split(" ")
	check = m[0][2:]

	if check.startswith("setting"):
		await BASE.moduls_Discord_.PROCESS.Mod.Settings.Base(BASE, message, kwargs)

	if check.startswith("addcom"):
		if await BASE.moduls.Utils.is_Mod(BASE, message):
			await BASE.moduls.Custom.add(BASE, message)
		else:
			await BASE.moduls.Utils.no_mod(BASE, message)

	if check.startswith("delcom"):
		if await BASE.moduls.Utils.is_Mod(BASE, message):
			await BASE.moduls.Custom.rem(BASE, message)
		else:
			await BASE.moduls.Utils.no_mod(BASE, message)

	if check.startswith("blacklist"):
		if await BASE.moduls.Utils.is_Mod(BASE, message):
			await BASE.moduls.Blacklist.base(BASE, message)
		else:
			await BASE.moduls.Utils.no_mod(BASE, message)

	if check.startswith("quote"):
		if await BASE.moduls.Utils.is_Mod(BASE, message):
			await BASE.moduls.Mod_Commands.quote.quote_base(BASE, message)
		else:
			await BASE.moduls.Utils.no_mod(BASE, message)

	if check.startswith("prune"):
		if await BASE.moduls.Utils.is_Mod(BASE, message):
			await BASE.moduls.Mod_Commands.prune.prune(BASE, message)
		else:
			await BASE.moduls.Utils.no_mod(BASE, message)

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

	if check.startswith("link"):
		if await BASE.moduls.Utils.is_Mod(BASE, message):
			await BASE.moduls.Mod_Commands.link.link(BASE, message)
		else:
			await BASE.moduls.Utils.no_mod(BASE, message)
