#BASE.moduls._Discord_.PROCESS.Owner

import asyncio, json, discord

class master(object):
	async def Base(BASE, message, kwargs):
		available = ['normal', 'mod', 'level', 'custom']
		m = message.content.lower().split()

		if len(m) == 1:
			return await BASE.phaaze.send_message(message.channel, ":warning: Missing option! Available are: {0}".format(", ".join("`"+l+"`" for l in available)))

		if m[1] == "normal":
			await master.normal(BASE, message, kwargs)

		elif m[1] == "mod":
			await master.mod(BASE, message, kwargs)

		elif m[1] == "level":
			await master.level(BASE, message, kwargs)

		elif m[1] == "custom":
			await master.custom(BASE, message, kwargs)

		else:
			av = ", ".join("`"+l+"`" for l in available)
			return await BASE.phaaze.send_message(message.channel, f":warning: `{m[1]}` is not a option! Available are: {av}")

	async def normal(BASE, message, kwargs):
		m = message.content.lower().split()

		if len(m) == 2:
			return await BASE.phaaze.send_message(message.channel, f":warning: `{m[0]} {m[1]}` is missing a valid state,\nTry: `on`/`off`")

		if m[2] in ['on', 'enable', 'yes']:
			state = False

		elif m[2] in ['off', 'dienable', 'no']:
			state = True

		else:
			return await BASE.phaaze.send_message(message.channel, f":warning: `{m[0]} {m[1]}` is missing a valid state,\nTry: `on`/`off`")

		BASE.PhaazeDB.update(
			of = "discord/server_setting",
			where = f"data['server_id'] == '{message.server.id}'",
			content = dict(owner_disable_normal=state)
		)
		state = "**disabled** :red_circle:" if state else "**enabled** :large_blue_circle:"
		return await BASE.phaaze.send_message(message.channel, f":white_check_mark: All Normal Commands are now Serverwide {state}")

	async def mod(BASE, message, kwargs):
		m = message.content.lower().split()

		if len(m) == 2:
			return await BASE.phaaze.send_message(message.channel, f":warning: `{m[0]} {m[1]}` is missing a valid state,\nTry: `on`/`off`")

		if m[2] in ['on', 'enable', 'yes']:
			state = False

		elif m[2] in ['off', 'dienable', 'no']:
			state = True

		else:
			return await BASE.phaaze.send_message(message.channel, f":warning: `{m[0]} {m[1]}` is missing a valid state,\nTry: `on`/`off`")

		BASE.PhaazeDB.update(
			of = "discord/server_setting",
			where = f"data['server_id'] == '{message.server.id}'",
			content = dict(owner_disable_mod=state)
		)
		state = "**disabled** :red_circle:" if state else "**enabled** :large_blue_circle:"
		return await BASE.phaaze.send_message(message.channel, f":white_check_mark: All Mod Commands are now Serverwide {state}")

	async def level(BASE, message, kwargs):
		m = message.content.lower().split()

		if len(m) == 2:
			return await BASE.phaaze.send_message(message.channel, f":warning: `{m[0]} {m[1]}` is missing a valid state,\nTry: `on`/`off`")

		if m[2] in ['on', 'enable', 'yes']:
			state = False

		elif m[2] in ['off', 'dienable', 'no']:
			state = True

		else:
			return await BASE.phaaze.send_message(message.channel, f":warning: `{m[0]} {m[1]}` is missing a valid state,\nTry: `on`/`off`")

		BASE.PhaazeDB.update(
			of = "discord/server_setting",
			where = f"data['server_id'] == '{message.server.id}'",
			content = dict(owner_disable_level=state)
		)
		state = "**disabled** :red_circle:" if state else "**enabled** :large_blue_circle:"
		return await BASE.phaaze.send_message(message.channel, f":white_check_mark: Levels are now Serverwide {state}")

	async def custom(BASE, message, kwargs):
		m = message.content.lower().split()

		if len(m) == 2:
			return await BASE.phaaze.send_message(message.channel, f":warning: `{m[0]} {m[1]}` is missing a valid state,\nTry: `on`/`off`")

		if m[2] in ['on', 'enable', 'yes']:
			state = False

		elif m[2] in ['off', 'dienable', 'no']:
			state = True

		else:
			return await BASE.phaaze.send_message(message.channel, f":warning: `{m[0]} {m[1]}` is missing a valid state,\nTry: `on`/`off`")

		BASE.PhaazeDB.update(
			of = "discord/server_setting",
			where = f"data['server_id'] == '{message.server.id}'",
			content = dict(owner_disable_custom=state)
		)
		state = "**disabled** :red_circle:" if state else "**enabled** :large_blue_circle:"
		return await BASE.phaaze.send_message(message.channel, f":white_check_mark: All custom commands are now Serverwide {state}")

class welcome(object):

	async def Base(BASE, message, kwargs):
		m = message.content.split(" ")

		#nothing
		if len(m) == 1:
			return await BASE.phaaze.send_message(message.channel, 	f":warning: Syntax Error!\nUsage: `{BASE.vars.PT * 3}welcome [Option]`\n\n"\
																	"`get` - The current welcome message + channel\n"\
																	"`get-priv` - The current private welcome message\n"\
																	"`get-raw` - The current unformated welcome message + channel\n"\
																	"`set` - Set the current welcome message\n"\
																	"`set-chan` - Set the channel where the message appears\n"\
																	"`set-priv` - Set a private message to new members\n"\
																	"`clear` - Removes channel and message\n"\
																	"`clear-priv` - Removes private message\n")

		#get
		elif m[1].lower() == "get":
			await welcome.get_welcome(BASE, message, kwargs, raw=False)
		#get-priv
		elif m[1].lower() == "get-priv":
			await welcome.get_welcome_priv(BASE, message, kwargs, raw=False)
		#get-priv
		elif m[1].lower() == "get-priv-raw":
			await welcome.get_welcome_priv(BASE, message, kwargs, raw=True)
		#get-raw
		elif m[1].lower() == "get-raw":
			await welcome.get_welcome(BASE, message, kwargs, raw=True)
		#set
		elif m[1].lower() == "set":
			await welcome.set_welcome(BASE, message, kwargs)
		#set-chan
		elif m[1].lower() == "set-chan":
			await welcome.set_welcome_chan(BASE, message, kwargs)
		#set-priv
		elif m[1].lower() == "set-priv":
			await welcome.priv_welcome(BASE, message, kwargs)
		#clear
		elif m[1].lower() == "clear":
			await welcome.clear_welcome(BASE, message, kwargs)
		#clear-priv
		elif m[1].lower() == "clear-priv":
			await welcome.clearpriv(BASE, message, kwargs)

		else:
			return await BASE.phaaze.send_message(message.channel, 	f":warning: `{m[1]}` is not available, try `{BASE.vars.PT * 3}welcome`")

	async def set_welcome(BASE, message, kwargs):
		m = message.content.split(" ")
		if len(m) == 2:
			return await BASE.phaaze.send_message(message.channel, 	f":warning: Syntax Error!\nUsage: `{BASE.vars.PT*3}welcome set [Stuff]`\n\n"\
																	"`[Stuff]` - The Text that appears in your set channel if a new member join\n\n"\
																	"You can use tokens in your `[Stuff]` that will be replaced by infos:\n"\
																	"`[name]` - The name of the new member\n"\
																	"`[mention]` - @mention the new member\n"\
																	"`[server]` - The server name\n"\
																	"`[count]` - Number the new member is")

		server_setting = kwargs['server_setting']

		entry = " ".join(g for g in m[2:])

		server_setting["welcome_msg"] = entry
		if server_setting.get("welcome_chan", None) == None:
			server_setting['welcome_chan'] = message.channel.id

		BASE.PhaazeDB.update(
			of="discord/server_setting",
			where=f"data['server_id'] == '{message.server.id}'",
			content=server_setting
		)

		phaaze_exc = await BASE.moduls._Discord_.Utils.return_real_me(BASE, message)

		entry = entry.replace("[name]", phaaze_exc.name)
		entry = entry.replace("[server]", message.server.name)
		entry = entry.replace("[count]", str(message.server.member_count))
		entry = entry.replace("[mention]", phaaze_exc.mention)

		chan = f"<#{server_setting['welcome_chan']}>"

		return await BASE.phaaze.send_message(message.channel, f":white_check_mark: New welcome message set! [In {chan}]\nExample with Phaaze:\n\n{entry}")

	async def set_welcome_chan(BASE, message, kwargs):
		m = message.content.split(" ")

		if len(m) == 2:
			chan = message.channel.id

		elif len(message.channel_mentions) >= 1:
			chan = message.channel_mentions[0].id

		BASE.PhaazeDB.update(
			of="discord/server_setting",
			where=f"data['server_id'] == '{message.server.id}'",
			content=dict(welcome_chan=chan)
		)

		return await BASE.phaaze.send_message(
			message.channel,
			f":white_check_mark: Welcome announce channel has been set to [<#{chan}>]")

	async def get_welcome(BASE, message, kwargs, raw=False):
		entry = kwargs['server_setting'].get('welcome_msg', None)
		if entry == None:
			return await BASE.phaaze.send_message(
				message.channel,
				":grey_exclamation: Seems like this Server currently don't has a welcome message")

		phaaze_exc = await BASE.moduls._Discord_.Utils.return_real_me(BASE, message)

		if not raw:
			entry = entry.replace("[name]", phaaze_exc.name)
			entry = entry.replace("[server]", message.server.name)
			entry = entry.replace("[count]", str(message.server.member_count))
			entry = entry.replace("[mention]", phaaze_exc.mention)

			entry = "Example with Phaaze:\n\n"+entry
		else:
			entry = "\n```"+entry+"```"

		chan = kwargs['server_setting'].get('welcome_chan', "1337")
		chan = f"<#{chan}>"

		return await BASE.phaaze.send_message(
			message.channel,
			f":grey_exclamation: Current welcome message [{chan}]\n{entry}")

	async def get_welcome_priv(BASE, message, kwargs, raw=False):
		entry = kwargs['server_setting'].get('welcome_msg_priv', None)
		if entry == None:
			return await BASE.phaaze.send_message(
				message.channel,
				":grey_exclamation: Seems like this Server currently don't has a private welcome message")

		phaaze_exc = await BASE.moduls._Discord_.Utils.return_real_me(BASE, message)

		if not raw:
			entry = entry.replace("[name]", phaaze_exc.name)
			entry = entry.replace("[server]", message.server.name)
			entry = entry.replace("[count]", str(message.server.member_count))
			entry = entry.replace("[mention]", phaaze_exc.mention)

			entry = "Example with Phaaze:\n\n"+entry
		else:
			entry = "\n```"+entry+"```"

		chan = kwargs['server_setting'].get('welcome_chan', "1337")
		chan = f"<#{chan}>"

		return await BASE.phaaze.send_message(
			message.channel,
			f":grey_exclamation: Current private welcome message [{chan}]\n{entry}")

	async def clear_welcome(BASE, message, kwargs):
		BASE.PhaazeDB.update(
			of="discord/server_setting",
			where=f"data['server_id'] == '{message.server.id}'",
			content=dict(welcome_msg=None, welcome_chan=None)
		)

		return await BASE.phaaze.send_message(
			message.channel,
			":white_check_mark: Welcome announce channel and message has been removed"
			)

	async def priv_welcome(BASE, message, kwargs):
		m = message.content.split(" ")
		if len(m) == 2:
			return await BASE.phaaze.send_message(message.channel, 	f":warning: Syntax Error!\nUsage: `{BASE.vars.PT*3}welcome set-priv [Stuff]`\n\n"\
																	"`[Stuff]` - The Text will send to a new member on join\n\n"\
																	"You can use tokens in your `[Stuff]` that will be replaced by infos:\n"\
																	"`[name]` - The name of the new member\n"\
																	"`[mention]` - @mention the new member\n"\
																	"`[server]` - The server name\n"\
																	"`[count]` - Number the new member is")

		server_setting = kwargs['server_setting']

		entry = " ".join(g for g in m[2:])

		server_setting["welcome_msg_priv"] = entry

		BASE.PhaazeDB.update(
			of="discord/server_setting",
			where=f"data['server_id'] == '{message.server.id}'",
			content=server_setting
		)

		phaaze_exc = await BASE.moduls._Discord_.Utils.return_real_me(BASE, message)

		entry = entry.replace("[name]", phaaze_exc.name)
		entry = entry.replace("[server]", message.server.name)
		entry = entry.replace("[count]", str(message.server.member_count))
		entry = entry.replace("[mention]", phaaze_exc.mention)

		return await BASE.phaaze.send_message(message.channel, f":white_check_mark: New welcome private message set!\nExample with Phaaze:\n\n{entry}")

	async def clearpriv(BASE, message, kwargs):
		BASE.PhaazeDB.update(
			of="discord/server_setting",
			where=f"data['server_id'] == '{message.server.id}'",
			content=dict(welcome_msg_priv=None)
		)

		return await BASE.phaaze.send_message(
			message.channel,
			":white_check_mark: Private welcome message has been removed"
		)

class leave(object):

	async def Base(BASE, message, kwargs):
		m = message.content.split(" ")

		#nothing
		if len(m) == 1:
			return await BASE.phaaze.send_message(message.channel, 	f":warning: Syntax Error!\nUsage: `{BASE.vars.PT * 3}leave [Option]`\n\n"\
																	"`get` - The current leave message + channel\n"\
																	"`get-raw` - The current unformated leave message + channel\n"\
																	"`set` - Set the current leave message\n"\
																	"`set-chan` - Set the channel where the message appears\n"\
																	"`clear` - Removes channel and message\n"\
																	"*(Leave Events can't send Private messages)*")

		#get
		elif m[1].lower() == "get":
			await leave.get_leave(BASE, message, kwargs, raw = False)
		#getraw
		elif m[1].lower() == "get-raw":
			await leave.get_leave(BASE, message, kwargs, raw = True)
		#set
		elif m[1].lower() == "set":
			await leave.set_leave(BASE, message, kwargs)
		#chan
		elif m[1].lower() == "set-chan":
			await leave.set_leave_chan(BASE, message, kwargs)
		#clear
		elif m[1].lower() == "clear":
			await leave.clear_leave(BASE, message, kwargs)

	async def set_leave(BASE, message, kwargs):
		m = message.content.split(" ")
		if len(m) == 2:
			return await BASE.phaaze.send_message(message.channel, 	f":warning: Syntax Error!\nUsage: `{BASE.vars.PT*3}welcome set [Stuff]`\n\n"\
																	"`[Stuff]` - The Text that appears in your set channel if a new member join\n\n"\
																	"You can use tokens in your `[Stuff]` that will be replaced by infos:\n"\
																	"`[name]` - The name of the new member\n"\
																	"`[mention]` - @mention the new member\n"\
																	"`[server]` - The server name\n"\
																	"`[count]` - Number the new member is")

		server_setting = kwargs['server_setting']

		entry = " ".join(g for g in m[2:])

		server_setting["leave_msg"] = entry
		if server_setting.get("leave_chan", None) == None:
			server_setting['leave_chan'] = message.channel.id

		BASE.PhaazeDB.update(
			of="discord/server_setting",
			where=f"data['server_id'] == '{message.server.id}'",
			content=server_setting
		)

		phaaze_exc = await BASE.moduls._Discord_.Utils.return_real_me(BASE, message)

		entry = entry.replace("[name]", phaaze_exc.name)
		entry = entry.replace("[server]", message.server.name)
		entry = entry.replace("[count]", str(message.server.member_count))
		entry = entry.replace("[mention]", phaaze_exc.mention)

		chan = f"<#{server_setting['leave_chan']}>"

		return await BASE.phaaze.send_message(message.channel, f":white_check_mark: New leave message set! [In {chan}]\nExample with Phaaze:\n\n{entry}")

	async def get_leave(BASE, message, kwargs, raw=False):
		entry = kwargs['server_setting'].get('leave_msg', None)
		if entry == None:
			return await BASE.phaaze.send_message(
				message.channel,
				":grey_exclamation: Seems like this Server currently don't has a leave message")

		phaaze_exc = await BASE.moduls._Discord_.Utils.return_real_me(BASE, message)

		if not raw:
			entry = entry.replace("[name]", phaaze_exc.name)
			entry = entry.replace("[server]", message.server.name)
			entry = entry.replace("[count]", str(message.server.member_count))
			entry = entry.replace("[mention]", phaaze_exc.mention)

			entry = "Example with Phaaze:\n\n"+entry
		else:
			entry = "\n```"+entry+"```"

		chan = kwargs['server_setting'].get('leave_chan', "1337")
		chan = f"<#{chan}>"

		return await BASE.phaaze.send_message(
			message.channel,
			f":grey_exclamation: Current leave message [{chan}]\n{entry}")

	async def set_leave_chan(BASE, message, kwargs):
		m = message.content.split(" ")

		if len(m) == 2:
			chan = message.channel.id

		elif len(message.channel_mentions) >= 1:
			chan = message.channel_mentions[0].id

		BASE.PhaazeDB.update(
			of="discord/server_setting",
			where=f"data['server_id'] == '{message.server.id}'",
			content=dict(leave_chan=chan)
		)

		return await BASE.phaaze.send_message(
			message.channel,
			f":white_check_mark: Leave announce channel has been set to [<#{chan}>]")

	async def clear_leave(BASE, message, kwargs):
		BASE.PhaazeDB.update(
			of="discord/server_setting",
			where=f"data['server_id'] == '{message.server.id}'",
			content=dict(leave_msg=None, leave_chan=None)
		)

		return await BASE.phaaze.send_message(
			message.channel,
			":white_check_mark: Leave announce channel and message has been removed"
			)

class logs(object):
	async def logs_base(BASE, message):
		m = message.content.split(" ")

		if len(m) == 1:
			file = await BASE.moduls.Utils.get_track_file(BASE, message.server.id)
			if file["track_chan"] == "":
				return await BASE.phaaze.send_message(message.channel, ":no_entry_sign: Before granting access to the log status you have to set a channel via `{0}{0}{0}logs chan`\n"\
				"	(It's recommended to set it to a non public channel)".format(BASE.vars.PT))

			all_c = [g.id for g in message.server.channels]
			if file["track_chan"] not in all_c:
				return await BASE.phaaze.send_message(message.channel, ":no_entry_sign: Before granting access to the log status you have to set a channel via `{0}{0}{0}logs chan`\n"\
				"	(It's recommended to set it to a non public channel)".format(BASE.vars.PT))

			f = "Channel: [{chan}]\nCurrent Trackstatus:\n\n\n"\
				"```Status - Keyword - Event:\n\n"\
				"{mes_del} - MDEL - Message deleted\n"\
				"{mes_edi} - MEDI - Message edited\n"\
				"{name} - NACH - Name change\n"\
				"{nich} - NICH - Nickname change\n"\
				"{role_u} - ROUP - Role update\n"\
				"{chan_u} - CHUP - Channel update\n"\
				"{custom_c} - CCED - Custom command edits\n"\
				"{join} - MEJO - Member joins\n"\
				"{leave} - MELE - Member leaves\n"\
				"{ban} - UBAN - User ban\n"\
				"{prune} - MOPR - Mod prunes messages```\n\n"\
				"`{PT}{PT}{PT}logs track [Keyword/alloff/allon]` - To switch options".format	(

						chan = "<#{0}>".format(file["track_chan"]),
						mes_del = "🔘" if file["message_deleted"] == 1 else "❌",
						mes_edi = "🔘" if file["message_edited"] == 1 else "❌",
						name = "🔘" if file["name_change"] == 1 else "❌",
						nich = "🔘" if file["nickname_change"] == 1 else "❌",
						role_u = "🔘" if file["role_update"] == 1 else "❌",
						chan_u = "🔘" if file["channel_update"] == 1 else "❌",
						custom_c = "🔘" if file["custom_commands"] == 1 else "❌",
						join = "🔘" if file["join"] == 1 else "❌",
						leave = "🔘" if file["leave"] == 1 else "❌",
						ban = "🔘" if file["banned"] == 1 else "❌",
						prune = "🔘" if file["prune"] == 1 else "❌",
						PT = BASE.vars.PT	)

			return await BASE.phaaze.send_message(message.channel, f)

		elif m[1].lower() == "chan":
			await logs.log_chan(BASE, message)

		elif m[1].lower() == "track":
			await logs.log_track(BASE, message)

		else:
			return await BASE.phaaze.send_message(message.channel, "`{0}` is not a option, use `{1}help logs` if you need help.".format(m[1], BASE.vars.PT))

	async def log_chan(BASE, message):
		m = message.content.split(" ")
		file = await BASE.moduls.Utils.get_track_file(BASE, message.server.id)

		if len(m) <= 2:
			chan = message.channel.id

		elif len(message.channel_mentions) >= 1:
			chan = message.channel_mentions[0].id
		else:
			return await BASE.phaaze.send_message(message.channel, ":warning: You can mention a channel or leave it empty to use the current.")

		file["track_chan"] = chan

		with open("SERVERFILES/TRACKFILES/{0}.json".format(message.server.id), "w") as save:
			json.dump(file, save)
			setattr(BASE.trackfiles, "track_"+message.server.id, file)

			return await BASE.phaaze.send_message(message.channel, "Logging channel set to [<#{0}>]".format(chan))

	async def log_track(BASE, message):
		m = message.content.split(" ")
		file = await BASE.moduls.Utils.get_track_file(BASE, message.server.id)
		if file["track_chan"] == "":
			return await BASE.phaaze.send_message(message.channel, ":no_entry_sign: Before granting access to the log status you have to set a channel via `{0}{0}{0}logs chan`\n"\
			"	(It's recommended to set it to a non public channel)".format(BASE.vars.PT))

		available = ["MDEL", "MEDI", "NACH", "NICH", "ROUP", "CHUP", "CCED", "QUED", "MEJO", "MELE", "UBAN", "MOPR", "ALLOFF", "ALLON"]

		if len(m) <= 2:
			return await BASE.phaaze.send_message(message.channel, ":warning: Missing Keyword after track, use only `{0}{0}{0}logs` to get the statuslist with keywords.".format(BASE.vars.PT))
		if m[2].upper() not in available:
			return await BASE.phaaze.send_message(message.channel, ":warning: `{1}` is not a Keyword  use `{0}{0}{0}logs` to get the statuslist with all keywords.".format(BASE.vars.PT, m[2]))

		def get_dict(mmm):
			if mmm == "MDEL":
				return "message_deleted"
			elif mmm == "MEDI":
				return "message_edited"
			elif mmm == "NACH":
				return "name_change"
			elif mmm == "NICH":
				return "nickname_change"
			elif mmm == "ROUP":
				return "role_update"
			elif mmm == "CHUP":
				return "channel_update"
			elif mmm == "CCED":
				return "custom_commands"
			elif mmm == "QUED":
				return "quotes"
			elif mmm == "MEJO":
				return"join"
			elif mmm == "MELE":
				return "leave"
			elif mmm == "UBAN":
				return "banned"
			elif mmm == "MOPR":
				return "prune"
			else:
				return None

		if m[2].lower() == "allon" or m[2].lower() == "alloff":
			for r in available:
				section = get_dict(r)
				if m[2].lower() == "allon":
					file[section] = 1
				if m[2].lower() == "alloff":
					file[section] = 0

			with open("SERVERFILES/TRACKFILES/{0}.json".format(message.server.id), "w") as save:
				json.dump(file, save)
				setattr(BASE.trackfiles, "track_"+message.server.id, file)

				return await BASE.phaaze.send_message(message.channel, ":white_check_mark: Everything has been **{status}**.".format(status = "enabled" if m[2].lower() == "allon" else "disabled"))

		else:
			section = get_dict(m[2].upper())

			if file[section] == 0:
				file[section] = 1
			else:
				file[section] = 0

			with open("SERVERFILES/TRACKFILES/{0}.json".format(message.server.id), "w") as save:
				json.dump(file, save)
				setattr(BASE.trackfiles, "track_"+message.server.id, file)

				return await BASE.phaaze.send_message(message.channel, ":white_check_mark: {word} has been **{status}**.".format(word = m[2].upper(), status = "enabled" if file[section] == 1 else "disabled"))

class autorole(object):
	async def base(BASE, message):
		m = message.content.split(" ")
		if len(m) == 1 or len(m) <= 2 and m[1].lower() == "get":
			#make method to get current roles
			await autorole._get_(BASE, message)

		elif m[1].lower() == "set":
			#make metod to set new roles
			await autorole._set_(BASE, message)

		elif m[1].lower() == "clear":
			#removes current role.
			await autorole._clear_(BASE, message)

		else:
			return await BASE.phaaze.send_message(message.channel, ":warning: `{0}` is not a option, available are: `get`, `set` and `clear`".format(m[1]))

	async def _get_(BASE, message):#get current set role
		file = await BASE.moduls.Utils.get_server_file(BASE, message.server.id)
		check = file["autorole_id"] = file.get("autorole_id", "")

		if check == "":
			return await BASE.phaaze.send_message(message.channel, ":exclamation: This server don't have a autorole set. \n 	Use `{0}{0}{0}autorole set [role]` to set one.".format(BASE.vars.PT))

		role = discord.utils.get(message.server.roles, id=check)

		if role == None:
			await autorole.not_present_role(BASE, message, file)

		else:
			return await BASE.phaaze.send_message(message.channel, ":exclamation: Current autorole is : `{0}`".format(role.name))

	async def _set_(BASE, message):
		m = message.content.split(" ")
		me = await BASE.moduls.Utils.return_real_me(BASE, message)

		if not me.server_permissions.manage_roles:
			return await BASE.phaaze.send_message(message.channel, ":no_entry_sign: Phaaze don't has a role with the `Manage Roles` Permission.")

		if len(m) == 2:
				return await BASE.phaaze.send_message(message.channel, ":warning: You need to define a role to set, you can do this via a role mention, role ID or full Role name. Try `{0}{0}getroles`".format(BASE.vars.PT))

		#by role mention
		if len(message.role_mentions) == 1:
			role = message.role_mentions[0]

		#by id
		elif m[2].isdigit():
			role = discord.utils.get(message.server.roles, id=m[2])
			if role == None:
				return await BASE.phaaze.send_message(message.channel, ":warning: No Role with the ID: `{0}` found.  Try `{1}{1}getroles`".format(m[2], BASE.vars.PT))

		#by name
		else:
			role = discord.utils.get(message.server.roles, name=" ".join(d for d in m[2:]))
			if role == None:
				return await BASE.phaaze.send_message(message.channel, ":warning: No Role with the Name: `{0}` found.  Try `{1}{1}getroles`".format(" ".join(d for d in m[2:]), BASE.vars.PT))

		if me.top_role < role:
			return await BASE.phaaze.send_message(message.channel, ":no_entry_sign: The Role: `{0}` is to high. Phaaze highest role has to be higher in hierarchy then: `{0}`".format(role.name.replace("`","´")))

		if role.managed:
			return await BASE.phaaze.send_message(message.channel, ":no_entry_sign: The Role: `{0}` is managed by a integration/app (Twitch, bot... etc), Phaaze can't give this Role to others.".format(role.name.replace("`","´")))

		file = await BASE.moduls.Utils.get_server_file(BASE, message.server.id)
		file["autorole_id"] = role.id

		#saving
		with open("SERVERFILES/{0}.json".format(message.server.id), "w") as save:
			json.dump(file, save)
			setattr(BASE.serverfiles, "server_"+message.server.id, file)
			return await BASE.phaaze.send_message(message.channel, ":white_check_mark: Autorole has been set to `{0}`".format(role.name))

	async def _clear_(BASE, message):
		file = await BASE.moduls.Utils.get_server_file(BASE, message.server.id)
		file["autorole_id"] = ""
		with open("SERVERFILES/{0}.json".format(message.server.id), "w") as save:
			json.dump(file, save)
			setattr(BASE.serverfiles, "server_"+message.server.id, file)
			return await BASE.phaaze.send_message(message.channel, ":white_check_mark: Autorole has been reset.")

	async def not_present_role(BASE, message, file): #reset role for server
		file["autorole_id"] = ""
		with open("SERVERFILES/{0}.json".format(message.server.id), "w") as save:
			json.dump(file, save)
			setattr(BASE.serverfiles, "server_"+message.server.id, file)
			return await BASE.phaaze.send_message(message.channel, ":warning: Seems like the Role that was set before no longer exist. Autorole has been reset.")

async def news(BASE, message):
	file = open("UTILS/server_channel_id_for_news.json", "r").read()
	file = json.loads(file)

	file["news_channels"] = file.get("news_channels", [])

	if message.channel.id in file["news_channels"]:
		file["news_channels"].remove(message.channel.id)
		try:
			await BASE.phaaze.send_message(message.channel, ":white_check_mark: Channel {} **removed** from PhaazeNews".format(message.channel.mention))
		except:
			pass

	else:
		file["news_channels"].append(message.channel.id)
		try:
			await BASE.phaaze.send_message(message.channel, ":white_check_mark: Channel {} **added** to PhaazeNews".format(message.channel.mention))
		except:
			pass

	with open("UTILS/server_channel_id_for_news.json", "w") as save:
		json.dump(file, save)
