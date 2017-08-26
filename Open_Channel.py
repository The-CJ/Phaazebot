##BASE.cmds.Open

import asyncio, requests, socket, json, discord

async def base(BASE, message):

	if len(message.author.roles) == 1 and message.server.id == "117801129496150019":
		role = discord.utils.get(message.server.roles, id="117808048919019527")
		await BASE.phaaze.add_roles(message.author, role)

	#blacklist
	await BASE.moduls.Blacklist.check(BASE, message)


	if message.edited_timestamp == None:
		#custom commands
		if message.author.id not in BASE.cooldown.Custom_CD:
			await BASE.moduls.Custom.get(BASE, message)
		#levels
		await BASE.moduls.levels.Discord.Base(BASE, message)

	"""Phaaze Commands"""
	#dev
	if message.content.startswith(BASE.vars.PT + BASE.vars.PT + BASE.vars.PT + BASE.vars.PT + BASE.vars.PT):
		if message.author.id == BASE.vars.CJ_ID: await BASE.cmds.CJ.base(BASE, message)

	#owner
	elif message.content.startswith(BASE.vars.PT + BASE.vars.PT + BASE.vars.PT):
		if message.author.id not in BASE.cooldown.Owner_CD:
			await BASE.cmds.OWNER.base(BASE, message)
			await BASE.cooldown.CD_Owner(message)

	#mod
	elif message.content.startswith(BASE.vars.PT + BASE.vars.PT):
		if message.author.id not in BASE.cooldown.Mod_CD:
			await BASE.cmds.MOD.base(BASE, message)
			await BASE.cooldown.CD_Mod(message)

	#normal
	elif message.content.startswith(BASE.vars.PT):
		if message.author.id not in BASE.cooldown.Normal_CD:
			await BASE.cmds.NORMAL.base(BASE, message)
			await BASE.cooldown.CD_Normal(message)

	#@phaazebot ai call
	if message.edited_timestamp == None:
		if message.content.startswith("<") and BASE.phaaze.user.id in message.content:
			m = message.content.split()[0]
			check = m.replace("!", "")
			check = check.replace("$", "")
			if check == BASE.phaaze.user.mention:
				return await BASE.moduls.cleverbot.discord(BASE, message)
