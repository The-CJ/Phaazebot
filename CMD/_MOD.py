##BASE.cmds.MOD

import asyncio

async def base(BASE, message):
	m = message.content.lower().split(" ")
	check = m[0][2:]


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

	if check.startswith("setting"):
		if await BASE.moduls.Utils.is_Mod(BASE, message):
			await BASE.moduls.Mod_Commands.settings(BASE, message)
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
