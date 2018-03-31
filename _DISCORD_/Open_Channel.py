##BASE.cmds.Open

import asyncio, requests, socket, json, discord

async def base(BASE, message):
	#R.o.D. Sys Overr.
	if len(message.author.roles) == 1 and message.server.id == "117801129496150019":
		role = discord.utils.get(message.server.roles, id="117808048919019527")
		await BASE.phaaze.add_roles(message.author, role)

	#get server files
	server_setting = await BASE.moduls.Utils.get_server_file(BASE, message.server.id)
	server_commands = await BASE.moduls.Utils.get_server_commands(BASE, message.server.id)

	#blacklist (Only, wenn links are banned or at least one word is in the blacklist)
	if server_setting.get('ban_links',False) or server_setting.get('blacklist', []) != []:
		await BASE.moduls.Blacklist.check(BASE, message, server_setting)

	#only execute when message is not edited
	if message.edited_timestamp == None:
		#custom commands
		await BASE.moduls.Custom.get(BASE, message, server_setting, server_commands)

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
