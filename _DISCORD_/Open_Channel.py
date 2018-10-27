##BASE.modules._Discord_.Open

import asyncio, discord

cooldown_normal = []
cooldown_mod = []
cooldown_owner = []

async def Base(BASE, message):
	#R.o.D. Sys Overr.
	if len(message.author.roles) == 1 and message.server.id == "117801129496150019":
		role = discord.utils.get(message.server.roles, id="117808048919019527")
		await BASE.discord.add_roles(message.author, role)

	# NOTE: -
	# MAYBE only call things when needed and not on every message, but i don't think its a big problem for now,
	# PhaazeDB can handle ~700 request/sec without a big delay. (Discord traffic on huge [5M user] servers: ~100-200 msg/sec)

	#get server files
	server_setting =  await BASE.modules._Discord_.Utils.get_server_setting(BASE, message.server.id)
	server_commands = await BASE.modules._Discord_.Utils.get_server_commands(BASE, message.server.id)
	server_levels =   await BASE.modules._Discord_.Utils.get_server_level(BASE, message.server.id)
	server_quotes =   await BASE.modules._Discord_.Utils.get_server_quotes(BASE, message.server.id)

	#blacklist (Only, when links are banned or at least one word is in the blacklist)
	if server_setting.get('ban_links', False) or server_setting.get('blacklist', []) != []:
		await BASE.modules._Discord_.Blacklist.check(BASE, message, server_setting)

	#only execute when message is not edited
	if message.edited_timestamp == None:
		#custom commands
		await BASE.modules._Discord_.Custom.get(BASE, message, server_setting, server_commands)

		#levels
		await BASE.modules._Discord_.Levels.Base(BASE, message, server_setting, server_levels)

	"""Phaaze Commands"""
	#dev
	if message.content.startswith(BASE.vars.TRIGGER_DISCORD * 5):
		if message.author.id in BASE.vars.developer_id:
			await BASE.modules._Discord_.CMD.Dev.Base(BASE, message, server_setting=server_setting, server_commands=server_commands, server_levels=server_levels, server_quotes=server_quotes)

	#owner
	elif message.content.startswith(BASE.vars.TRIGGER_DISCORD * 3):
		if message.author.id not in cooldown_owner:
			asyncio.ensure_future(cooldown_Owner(BASE, message))
			await BASE.modules._Discord_.CMD.Owner.Base(BASE, message, server_setting=server_setting, server_commands=server_commands, server_levels=server_levels, server_quotes=server_quotes)

	#mod
	elif message.content.startswith(BASE.vars.TRIGGER_DISCORD * 2):
		if message.author.id not in cooldown_mod:
			asyncio.ensure_future(cooldown_Mod(BASE, message))
			await BASE.modules._Discord_.CMD.Mod.Base(BASE, message, server_setting=server_setting, server_commands=server_commands, server_levels=server_levels, server_quotes=server_quotes)

	#normal
	elif message.content.startswith(BASE.vars.TRIGGER_DISCORD):
		if message.author.id not in cooldown_normal:
			asyncio.ensure_future(cooldown_Normal(BASE, message))
			await BASE.modules._Discord_.CMD.Normal.Base(BASE, message, server_setting=server_setting, server_commands=server_commands, server_levels=server_levels, server_quotes=server_quotes)

	#@phaazebot ai call
	if message.edited_timestamp == None:
		if message.content.startswith("<") and BASE.discord.user.id in message.content:
			m = message.content.split()[0]
			check = m.replace("!", "")
			check = check.replace("$", "")
			if check == BASE.discord.user.mention:
				return await BASE.discord.send_message(message.channel, ":no_entry_sign: Phaaze AI Moduls not avalible for now.")

async def cooldown_Normal(BASE, m):
	cooldown_normal.append(m.author.id)
	await asyncio.sleep(BASE.limit.DISCORD_NORMAL_COOLDOWN)
	try:
		cooldown_normal.remove(m.author.id)
	except:
		pass

async def cooldown_Mod(BASE, m):
	cooldown_mod.append(m.author.id)
	await asyncio.sleep(BASE.limit.DISCORD_MOD_COOLDOWN)
	try:
		cooldown_mod.remove(m.author.id)
	except:
		pass

async def cooldown_Owner(BASE, m):
	cooldown_owner.append(m.author.id)
	await asyncio.sleep(BASE.limit.DISCORD_OWNER_COOLDOWN)
	try:
		cooldown_owner.remove(m.author.id)
	except:
		pass
