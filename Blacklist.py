##BASE.moduls.Blacklist

import asyncio, json, re
link_contents = ["http", ".de", "://", ".com", ".net", ".tv", "www."]

async def check(BASE, message):
	if await BASE.moduls.Utils.is_Mod(BASE, message): return
	me = await BASE.moduls.Utils.return_real_me(BASE, message)
	phaaze_perms = message.channel.permissions_for(me)
	if not phaaze_perms.manage_messages:
		return
	file = await BASE.moduls.Utils.get_server_file(BASE, message.server.id)

	file["blacklist"] = file.get("blacklist", [])
	file["ban_links"] = file.get("ban_links", False)
	file["link_whitelist"] = file.get("link_whitelist", [])
	file["allow_link_role"] = file.get("allow_link_role", None)

	punishment_level = file.get("punishment_level", "delete")
	m = message.content.lower().split(" ")
	if file["ban_links"]:
		for word in m:
			for cont in link_contents:
				if cont in word:
					try:
						if any([True for WORD in file["link_whitelist"] if WORD in word]):
							pass
						elif file["allow_link_role"] in [r.id for r in message.author.roles]:
							pass
						else:
							await BASE.phaaze.delete_message(message)
							break

					except:
						pass

	for word in file["blacklist"]:
		if word.lower() in message.content.lower():
			try:
				if punishment_level == "delete":
					await BASE.phaaze.delete_message(message)

				elif punishment_level == "kick":
					await BASE.phaaze.delete_message(message)
					await BASE.phaaze.kick(message.author)

				elif punishment_level == "ban":
					await BASE.phaaze.delete_message(message)
					await BASE.phaaze.ban(message.author, delete_message_days=1)

			except:
				pass

async def base(BASE, message):
	me = await BASE.moduls.Utils.return_real_me(BASE, message)
	if not me.server_permissions.manage_messages:
		return await BASE.phaaze.send_message(message.channel, ":no_entry_sign: Phaaze need the `Manage messages` permission to execute Blacklist commands.")


	m = message.content.lower().split(" ")

	if len(m) == 1:
		r = ":warning: Syntax Error!\nUsage: `{0}{0}blacklist [Option]`\n\n"\
			"Options:\n"\
			"`punishment` - Set the way Phaaze handles blacklisted words\n"\
			"`get` - Get all words / phrase that are on the blacklist\n"\
			"`add` - Add a word / phrase to the blacklist\n"\
			"`rem` - Remove a word / phrase from the blacklist\n"\
			"`clear` - Remove all word / phrases, so the blacklist is empty".format(BASE.vars.PT)
		a = await BASE.phaaze.send_message(message.channel, r)

	elif m[1] == "get":
		await get(BASE, message)
	elif m[1] == "add":
		await add(BASE, message)
	elif m[1] == "rem":
		await rem(BASE, message)
	elif m[1] == "clear":
		await clear(BASE, message)
	elif m[1] == "punishment":
		await punishment(BASE, message, me)
	else:
		return await BASE.phaaze.send_message(message.channel, ":warning: `{0}` is not a option.".format(m[1]))

async def get(BASE, message):
	file = await BASE.moduls.Utils.get_server_file(BASE, message.server.id)

	try:
		file["blacklist"] = file["blacklist"]
	except:
		file["blacklist"] = []

	if len(file["blacklist"]) == 0:
		return await BASE.phaaze.send_message(message.channel, "No words are banned! :thumbsup:")

	else:
		return await BASE.phaaze.send_message(message.channel,
											"A list of all banned words and phrases on the server.\n\n```{0}```".format(", ".join(b for b in file["blacklist"])))

async def add(BASE, message):
	m = message.content.lower().split(" ")

	if len(m) == 2:
		return await BASE.phaaze.send_message(message.channel, ":warning: You need to define a word or a phrase to add.")

	file = await BASE.moduls.Utils.get_server_file(BASE, message.server.id)

	try:
		file["blacklist"] = file["blacklist"]
	except:
		file["blacklist"] = []

	word = " ".join(l for l in m[2:])

	if len(m[2:]) > 1:
		type_ = "phrase"
	else:
		type_ = "word"

	if word in file["blacklist"]:
		return await BASE.phaaze.send_message(message.channel, ":warning: This {0} is already in the blacklist.".format(type_))
	else:
		file["blacklist"].append(word)

	with open("SERVERFILES/{0}.json".format(message.server.id), "w") as save:
		json.dump(file, save)
		setattr(BASE.serverfiles, "server_"+message.server.id, file)

		return await BASE.phaaze.send_message(message.channel, ":white_check_mark: The {0}: `{1}` has been added.".format(type_, word))

async def rem(BASE, message):
	m = message.content.lower().split(" ")

	if len(m) == 2:
		return await BASE.phaaze.send_message(message.channel, ":warning: You need to define a word or a phrase you wanna remove.")

	file = await BASE.moduls.Utils.get_server_file(BASE, message.server.id)

	try:
		file["blacklist"] = file["blacklist"]
	except:
		file["blacklist"] = []

	word = " ".join(l for l in m[2:])

	if len(m[2:]) > 1:
		type_ = "phrase"
	else:
		type_ = "word"

	if word in file["blacklist"]:
		file["blacklist"].remove(word)
	else:
		return await BASE.phaaze.send_message(message.channel, ":warning: `{0}` is not in the blacklist.".format(word))

	with open("SERVERFILES/{0}.json".format(message.server.id), "w") as save:
		json.dump(file, save)
		setattr(BASE.serverfiles, "server_"+message.server.id, file)

		return await BASE.phaaze.send_message(message.channel, ":white_check_mark: The {0}: `{1}` has been removed.".format(type_, word))

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

async def punishment(BASE, message, perms):
	m = message.content.lower().split(" ")
	file = await BASE.moduls.Utils.get_server_file(BASE, message.server.id)

	file["punishment_level"] = file.get("punishment_level", "delete")

	if len(m) == 2:
		return await BASE.phaaze.send_message(message.channel, ":grey_exclamation: Current punishment level: `{0}`\nType: `{1}{1}blacklist punishment (delete/kick/ban)` to change".format(file["punishment_level"], BASE.vars.PT))

	if m[2] == "delete":
		with open("SERVERFILES/{0}.json".format(message.server.id), "w") as save:
			file["punishment_level"] = "delete"
			json.dump(file, save)
			setattr(BASE.serverfiles, "server_"+message.server.id, file)
			return await BASE.phaaze.send_message(message.channel, ":white_check_mark: Punishment Level set to: \"`delete`\". Phaaze will only **delete** blacklisted messages")

	elif m[2] == "kick":
		if not perms.server_permissions.kick_members:
			return await BASE.phaaze.send_message(message.channel, ":no_entry_sign: Phaaze need the `Kick Members` permission to execute kick commands.")

		with open("SERVERFILES/{0}.json".format(message.server.id), "w") as save:
			file["punishment_level"] = "kick"
			json.dump(file, save)
			setattr(BASE.serverfiles, "server_"+message.server.id, file)
			return await BASE.phaaze.send_message(message.channel, ":white_check_mark: Punishment Level set to: \"`kick`\". Phaaze will **delete** blacklisted messages **and kick** the author")

	elif m[2] == "ban":
		if not perms.server_permissions.ban_members:
			return await BASE.phaaze.send_message(message.channel, ":no_entry_sign: Phaaze need the `Ban Members` permission to execute kick commands.")

		with open("SERVERFILES/{0}.json".format(message.server.id), "w") as save:
			file["punishment_level"] = "ban"
			json.dump(file, save)
			setattr(BASE.serverfiles, "server_"+message.server.id, file)
			return await BASE.phaaze.send_message(message.channel, ":white_check_mark: Punishment Level set to: \"`ban`\". Phaaze will **delete** blacklisted messages **and ban** the author")

	else:
		return await BASE.phaaze.send_message(message.channel, "`{0}` is not a option".format(m[2]))
