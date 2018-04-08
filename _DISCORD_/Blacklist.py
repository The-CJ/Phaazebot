##BASE.moduls._Discord_.Blacklist

import asyncio, json
link_contents = ["http", ".de", "://", ".com", ".net", ".tv", "www."]

async def check(BASE, message, server_setting):
	me = await BASE.moduls._Discord_.Utils.return_real_me(BASE, message)
	phaaze_perms = message.channel.permissions_for(me)

	if not phaaze_perms.manage_messages: return

	if await BASE.moduls._Discord_.Utils.is_Mod(BASE, message): return

	blacklist = server_setting.get("blacklist", [])
	ban_links = server_setting.get("ban_links", False)
	link_whitelist = server_setting.get("link_whitelist", [])
	allow_link_role = server_setting.get("allow_link_role", [])
	punishment_level = server_setting.get("punishment_level", "delete")

	punish = False

	#Link are not allowed
	if ban_links:

		#has not a role that allows links
		if not any([True if role.id in allow_link_role else False for role in message.author.roles]):

			#contains a link that is not allowed
			for word in message.content.lower().split(' '):
				if any([True if linkpart in word and not word in link_whitelist else False for linkpart in link_contents]):
					punish = True
					break

	#Word Blacklist
	for word in blacklist:
		if word.lower() in message.content.lower():
			punish = True
			break

	if punish:
		try:
			if punishment_level == "delete":
				await BASE.phaaze.delete_message(message)
			elif punishment_level == "kick":
				await BASE.phaaze.delete_message(message)
				await BASE.phaaze.kick(message.author)
			elif punishment_level == "ban":
				await BASE.phaaze.ban(message.author, delete_message_days=1)

		except:
			pass

async def Base(BASE, message, kwargs):
	me = await BASE.moduls._Discord_.Utils.return_real_me(BASE, message)
	phaaze_perms = message.channel.permissions_for(me)

	if not phaaze_perms.manage_messages:
		return await BASE.phaaze.send_message(message.channel, ":no_entry_sign: Phaaze need the `Manage messages` permission to execute Blacklist commands.")

	m = message.content.lower().split(" ")

	if len(m) == 1:
		r = f":warning: Syntax Error!\nUsage: `{BASE.vars.PT}blacklist [Option]`\n\n"\
			"`punishment` - Set the way Phaaze handles blacklisted words or links\n"\
			"`get` - Get all words / phrase on the blacklist\n"\
			"`add` - Add a word / phrase to the blacklist\n"\
			"`rem` - Remove a word / phrase from the blacklist\n"\
			"`clear` - Remove all word / phrasesfrom the blacklist\n"\
			"`link-toggle` - Turns link protection on or off\n"\
			"`link-get` - Get all links that are whitelisted\n"\
			"`link-allow` - Add a role to post any links\n"\
			"`link-disallow` - Remove a role to post any links\n"\
			"`link-add` - Add a link to the whitelist\n"\
			"`link-rem` - Remove a link from the whitelist\n"\
			"`link-clear` - Remove all whitelisted links"
		return await BASE.phaaze.send_message(message.channel, r)

	elif m[1] == "punishment":
		await punishment(BASE, message, kwargs, me)
	elif m[1] == "get":
		await get(BASE, message, kwargs)
	elif m[1] == "add":
		await add(BASE, message, kwargs)
	elif m[1] == "rem":
		await rem(BASE, message, kwargs)
	elif m[1] == "clear": #TODO:
		await clear(BASE, message, kwargs)
	elif m[1] == "link-toggle": #TODO:
		await Link.toggle(BASE, message, kwargs)
	elif m[1] == "link-get": #TODO:
		await Link.get(BASE, message, kwargs)
	elif m[1] == "link-allow": #TODO:
		await Link.allow(BASE, message, kwargs)
	elif m[1] == "link-disallow": #TODO:
		await Link.disallow(BASE, message, kwargs)
	elif m[1] == "link-add": #TODO:
		await Link.add(BASE, message, kwargs)
	elif m[1] == "link-rem": #TODO:
		await Link.rem(BASE, message, kwargs)
	elif m[1] == "link-clear": #TODO:
		await Link.clear(BASE, message, kwargs)
	else:
		return await BASE.phaaze.send_message(message.channel, ":warning: `{0}` is not a option.".format(m[1]))

async def punishment(BASE, message, kwargs, perms):
	m = message.content.lower().split(" ")

	if len(m) == 2:
		blacklist_punishment = kwargs.get('server_setting', {}).get("blacklist_punishment", "delete")
		return await BASE.phaaze.send_message(message.channel, f":grey_exclamation: Current punishment level: `{blacklist_punishment}`\nType: `{BASE.vars.PT}blacklist punishment (delete/kick/ban)` to change")

	if m[2] == "delete":
		BASE.PhaazeDB.update(
			of="discord/server_setting",
			where=f"data['server_id'] == '{message.server.id}'",
			content=dict(blacklist_punishment = "delete"))
		return await BASE.phaaze.send_message(message.channel, ":white_check_mark: Punishment Level set to: `delete`.\nPhaaze will only **delete** the message")

	elif m[2] == "kick":
		if not perms.server_permissions.kick_members:
			return await BASE.phaaze.send_message(message.channel, ":no_entry_sign: Phaaze need the `Kick Members` permission to execute kick commands.")

		BASE.PhaazeDB.update(
			of="discord/server_setting",
			where=f"data['server_id'] == '{message.server.id}'",
			content=dict(blacklist_punishment = "kick"))
		return await BASE.phaaze.send_message(message.channel, ":white_check_mark: Punishment Level set to: `kick`.\nPhaaze will **delete** the messages **and kick** the author")

	elif m[2] == "ban":
		if not perms.server_permissions.ban_members:
			return await BASE.phaaze.send_message(message.channel, ":no_entry_sign: Phaaze need the `Ban Members` permission to execute kick commands.")

		BASE.PhaazeDB.update(
			of="discord/server_setting",
			where=f"data['server_id'] == '{message.server.id}'",
			content=dict(blacklist_punishment = "ban"))
		return await BASE.phaaze.send_message(message.channel, ":white_check_mark: Punishment Level set to: `ban`.\nPhaaze will **delete** the messages **and ban** the author")

	else:
		return await BASE.phaaze.send_message(message.channel, "`{0}` is not a option".format(m[2]))

async def get(BASE, message, kwargs):

	blacklist = kwargs.get('server_setting', {}).get('blacklist', [])

	if len(blacklist) == 0:
		return await BASE.phaaze.send_message(message.channel, "No words are banned! :thumbsup:")

	else:
		l = ", ".join(b for b in blacklist)
		return await BASE.phaaze.send_message(message.channel, f"A list of all banned words and phrases on the server.\n\n```{l}```")

async def add(BASE, message, kwargs):
	m = message.content.lower().split(" ")

	if len(m) == 2:
		return await BASE.phaaze.send_message(message.channel, ":warning: You need to define a word or a phrase to add.")

	blacklist = kwargs.get('server_setting', {}).get('blacklist', [])

	word = " ".join(l for l in m[2:])

	if len(m[2:]) > 1:
		type_ = "phrase"
	else:
		type_ = "word"

	if word in blacklist:
		return await BASE.phaaze.send_message(message.channel, ":warning: This {0} is already in the blacklist.".format(type_))
	else:
		blacklist.append(word.lower())

	BASE.PhaazeDB.update(
		of="discord/server_setting",
		where=f"data['server_id'] == '{message.server.id}'",
		content=dict(blacklist=blacklist)
	)

	return await BASE.phaaze.send_message(message.channel, f":white_check_mark: The {type_}: `{word}` has been added to the blacklist.")

async def rem(BASE, message, kwargs):
	m = message.content.lower().split(" ")

	if len(m) == 2:
		return await BASE.phaaze.send_message(message.channel, ":warning: You need to define a word or a phrase you wanna remove.")

	blacklist = kwargs.get('server_setting', {}).get('blacklist', [])

	word = " ".join(l for l in m[2:])

	if len(m[2:]) > 1:
		type_ = "phrase"
	else:
		type_ = "word"

	if word in blacklist:
		blacklist.remove(word)
	else:
		return await BASE.phaaze.send_message(message.channel, f":warning: `{word}` is not in the blacklist.")

	BASE.PhaazeDB.update(
		of="discord/server_setting",
		where=f"data['server_id'] == '{message.server.id}'",
		content=dict(blacklist=blacklist)
	)

	return await BASE.phaaze.send_message(message.channel, f":white_check_mark: The {type_}: `{word}` has been removed from the blacklist.")

async def clear(BASE, message):

	h = await BASE.phaaze.send_message(message.channel, ":warning: Are you sure you wanna clear the blacklist completly?\n\n:regional_indicator_y:/:regional_indicator_n:")

	def g(m):
		if m.content.lower().startswith("y"):
			return True
		else:
			return False

	u = await BASE.phaaze.wait_for_message(timeout=30, author=message.author, channel=message.channel, check=g)

	if u is not None:
		file = await BASE.moduls.Utils.get_server_file(BASE, message.server.id)

		file["blacklist"] = []

		with open("SERVERFILES/{0}.json".format(message.server.id), "w") as save:
			json.dump(file, save)
			setattr(BASE.serverfiles, "server_"+message.server.id, file)

		await BASE.phaaze.edit_message(h, new_content=":white_check_mark: Blacklist cleared.")

class Link(object):

	async def toggle(BASE, message):

		file = await BASE.moduls.Utils.get_server_file(BASE, message.server.id)

		file["ban_links"] = file.get("ban_links", False)

		if file["ban_links"]:
			file["ban_links"] = False
			try: await BASE.phaaze.send_message(message.channel, ":white_check_mark: Link protection has been disabled, all links allowed. :red_circle:")
			except: pass

		else:
			file["ban_links"] = True
			try: await BASE.phaaze.send_message(message.channel, ":white_check_mark: Link protection has been enabled, all links will get deleted. :large_blue_circle:")
			except: pass

		with open("SERVERFILES/{0}.json".format(message.server.id), "w") as save:
			json.dump(file, save)
			setattr(BASE.serverfiles, "server_"+message.server.id, file)

	async def whitelist(BASE, message):

		file = await BASE.moduls.Utils.get_server_file(BASE, message.server.id)

		file["link_whitelist"] = file.get("link_whitelist", [])

		if len(file["link_whitelist"]) == 0:
			return await BASE.phaaze.send_message(message.channel, ":information_source: No links are whitelisted, every link gets deleted")

		b = ", ".join("`"+word+"`" for word in file["link_whitelist"])
		return await BASE.phaaze.send_message(message.channel, ":information_source: Allowed Links must contain: " + b)

	async def add(BASE, message):
		m = message.content.lower().split(" ")
		file = await BASE.moduls.Utils.get_server_file(BASE, message.server.id)

		file["link_whitelist"] = file.get("link_whitelist", [])

		file["link_whitelist"].append(m[2])

		with open("SERVERFILES/{0}.json".format(message.server.id), "w") as save:
			json.dump(file, save)
			setattr(BASE.serverfiles, "server_"+message.server.id, file)
			return await BASE.phaaze.send_message(message.channel, ":white_check_mark: {0} has been added to the whitelist, link that contain this will not get deleted.".format(m[2]))

	async def rem(BASE, message):
		m = message.content.lower().split(" ")
		file = await BASE.moduls.Utils.get_server_file(BASE, message.server.id)

		file["link_whitelist"] = file.get("link_whitelist", [])

		if m[2] in file["link_whitelist"]:
			file["link_whitelist"].remove(m[2])

		else:
			return await BASE.phaaze.send_message(message.channel, ":warning: {0} is not in the whitelist.".format(m[3]))

		with open("SERVERFILES/{0}.json".format(message.server.id), "w") as save:
			json.dump(file, save)
			setattr(BASE.serverfiles, "server_"+message.server.id, file)
			return await BASE.phaaze.send_message(message.channel, "white_check_mark: {0} has been removed from the whitelist.".format(m[3]))

	async def allow(BASE, message):
		m = message.content.lower().split(" ")
		file = await BASE.moduls.Utils.get_server_file(BASE, message.server.id)

		file["allow_link_role"] = file.get("allow_link_role", None)

		if len(message.role_mentions) != 0:
			file["allow_link_role"] = message.role_mentions[0].id
		else:
			return await BASE.phaaze.send_message(message.channel, ":warning: Missing Role Mention")

		with open("SERVERFILES/{0}.json".format(message.server.id), "w") as save:
			json.dump(file, save)
			setattr(BASE.serverfiles, "server_"+message.server.id, file)
			return await BASE.phaaze.send_message(message.channel, ":white_check_mark: {0} has been set to link-allowed-role.".format(message.role_mentions[0].name))
