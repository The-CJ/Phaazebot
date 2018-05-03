#BASE.moduls._Discord_.CMD.Mod

import asyncio

CMDs = ['setting', 'addcom', 'delcom', 'blacklist', 'quote', 'prune', 'level', 'serverinfo', 'getrole']

class Forbidden(object):
	async def no_mod(BASE, message, kwargs):
		m = await BASE.discord.send_message(message.channel, ":no_entry_sign: You can not use Mod Commands")
		await asyncio.sleep(2.5)
		await BASE.discord.delete_message(m)

	async def owner_disabled_mod(BASE, message, kwargs):
		m = await BASE.discord.send_message(message.channel, ":no_entry_sign: The Serverowner disabled Mod-commands, only the Serverowner can use them")
		await asyncio.sleep(2.5)
		await BASE.discord.delete_message(m)

async def Base(BASE, message, **kwargs):
	m = message.content.lower().split(" ")
	check = m[0][2:]

	if not await BASE.moduls._Discord_.Utils.is_Mod(BASE, message):
		if any([True if check.startswith(cmd) else False for cmd in CMDs]):
			asyncio.ensure_future(Forbidden.no_mod(BASE, message, kwargs))
			return

	if not await BASE.moduls._Discord_.Utils.is_Owner(BASE, message) and kwargs.get('server_setting', {}).get('owner_disable_mod', False):
		if any([True if check.startswith(cmd) else False for cmd in CMDs]):
			asyncio.ensure_future(Forbidden.owner_disabled_mod(BASE, message, kwargs))
			return

	# # #

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

	if check.startswith("level"):
		return await BASE.moduls._Discord_.PROCESS.Mod.Level.Base(BASE, message, kwargs)

	if check.startswith("serverinfo"):
		return await BASE.moduls._Discord_.PROCESS.Mod.Utils.serverinfo(BASE, message, kwargs)

	if check.startswith("getrole"):
		return await BASE.moduls._Discord_.PROCESS.Mod.Utils.getroles(BASE, message, kwargs)
