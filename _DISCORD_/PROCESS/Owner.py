#BASE.moduls._Discord_.PROCESS.Owner

import asyncio, discord

class Master(object):
	async def Base(BASE, message, kwargs):
		available = ['normal', 'mod', 'level', 'custom']
		m = message.content.lower().split()

		if len(m) == 1:
			return await BASE.phaaze.send_message(message.channel, ":warning: Missing option! Available are: {0}".format(", ".join("`"+l+"`" for l in available)))

		if m[1] == "normal":
			await Master.normal(BASE, message, kwargs)

		elif m[1] == "mod":
			await Master.mod(BASE, message, kwargs)

		elif m[1] == "level":
			await Master.level(BASE, message, kwargs)

		elif m[1] == "custom":
			await Master.custom(BASE, message, kwargs)

		else:
			av = ", ".join("`"+l+"`" for l in available)
			return await BASE.phaaze.send_message(message.channel, f":warning: `{m[1]}` is not a option! Available are: {av}")

	async def normal(BASE, message, kwargs):
		m = message.content.lower().split()

		if len(m) == 2:
			return await BASE.phaaze.send_message(message.channel, f":warning: `{m[0]} {m[1]}` is missing a valid state,\nTry: `on`/`off`")

		if m[2] in ['on', 'enable', 'yes']:
			state = False

		elif m[2] in ['off', 'disable', 'no']:
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

		elif m[2] in ['off', 'disable', 'no']:
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

		elif m[2] in ['off', 'disable', 'no']:
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

		elif m[2] in ['off', 'disable', 'no']:
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

class Welcome(object):

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
			await Welcome.get_welcome(BASE, message, kwargs, raw=False)
		#get-priv
		elif m[1].lower() == "get-priv":
			await Welcome.get_welcome_priv(BASE, message, kwargs, raw=False)
		#get-priv
		elif m[1].lower() == "get-priv-raw":
			await Welcome.get_welcome_priv(BASE, message, kwargs, raw=True)
		#get-raw
		elif m[1].lower() == "get-raw":
			await Welcome.get_welcome(BASE, message, kwargs, raw=True)
		#set
		elif m[1].lower() == "set":
			await Welcome.set_welcome(BASE, message, kwargs)
		#set-chan
		elif m[1].lower() == "set-chan":
			await Welcome.set_welcome_chan(BASE, message, kwargs)
		#set-priv
		elif m[1].lower() == "set-priv":
			await Welcome.priv_welcome(BASE, message, kwargs)
		#clear
		elif m[1].lower() == "clear":
			await Welcome.clear_welcome(BASE, message, kwargs)
		#clear-priv
		elif m[1].lower() == "clear-priv":
			await Welcome.clearpriv(BASE, message, kwargs)

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

class Leave(object):

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
			await Leave.get_leave(BASE, message, kwargs, raw = False)
		#getraw
		elif m[1].lower() == "get-raw":
			await Leave.get_leave(BASE, message, kwargs, raw = True)
		#set
		elif m[1].lower() == "set":
			await Leave.set_leave(BASE, message, kwargs)
		#chan
		elif m[1].lower() == "set-chan":
			await Leave.set_leave_chan(BASE, message, kwargs)
		#clear
		elif m[1].lower() == "clear":
			await Leave.clear_leave(BASE, message, kwargs)

		else:
			return await BASE.phaaze.send_message(message.channel, 	f":warning: `{m[1]}` is not available, try `{BASE.vars.PT * 3}leave`")

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

class Autorole(object):

	async def Base(BASE, message, kwargs):
		m = message.content.split(" ")
		if len(m) == 1:
			return await BASE.phaaze.send_message(message.channel, 	f":warning: Syntax Error!\nUsage: `{BASE.vars.PT * 3}autorole [Option]`\n\n"\
																	"`get` - The current autorole\n"\
																	"`set` - Set new autorole\n"\
																	"`clear` - Removes the autorole\n"\
																	"*(Thís role gets applied to new members)*")

		if m[1].lower() == "get":
			await Autorole._get_(BASE, message, kwargs)

		elif m[1].lower() == "set":
			await Autorole._set_(BASE, message, kwargs)

		elif m[1].lower() == "clear":
			await Autorole._clear_(BASE, message, kwargs)

		else:
			return await BASE.phaaze.send_message(message.channel, 	f":warning: `{m[1]}` is not available, try `{BASE.vars.PT * 3}autorole`")

	async def _get_(BASE, message, kwargs):
		current = kwargs.get('server_setting', {}).get('autorole', None)
		if current == None:
			return await BASE.phaaze.send_message(message.channel, f":exclamation: This server don't have a autorole set. \n 	Use `{BASE.vars.PT*3}autorole set [role]` to set one.")

		role = discord.utils.get(message.server.roles, id=current)

		if role == None:
			return await BASE.phaaze.send_message(message.channel, f":grey_question: Strange, it seems like there was a autorole set, but it could not be found. \n 	Use `{BASE.vars.PT*3}autorole set [role]` to set a new one.")

		else:
			if role.name.lower() == "@everyone": role.name = "[everyone]"
			return await BASE.phaaze.send_message(message.channel, f":exclamation: Current autorole is : `{role.name}`")

	async def _set_(BASE, message, kwargs):
		m = message.content.split(" ")
		me = await BASE.moduls._Discord_.Utils.return_real_me(BASE, message)

		if not me.server_permissions.manage_roles:
			return await BASE.phaaze.send_message(
				message.channel,
				":no_entry_sign: Phaaze don't has a role with the `Manage Roles` Permission."
			)

		if len(m) == 2:
			return await BASE.phaaze.send_message(
				message.channel,
				":warning: You need to define a role to set, you can do this via a role mention, role ID or full Role name.")

		#by role mention
		if len(message.role_mentions) == 1:
			role = message.role_mentions[0]

		#by id
		elif m[2].isdigit():
			role = discord.utils.get(message.server.roles, id=m[2])
			if role == None:
				return await BASE.phaaze.send_message(
					message.channel,
					f":warning: No Role with the ID: `{m[2]}` found"
				)

		#by name
		else:
			r_n = " ".join(d for d in m[2:])
			role = discord.utils.get(message.server.roles, name=r_n)
			if role == None:
				return await BASE.phaaze.send_message(
					message.channel,
					f":warning: No Role with the Name: `{r_n}` found."
				)

		if me.top_role < role:
			return await BASE.phaaze.send_message(
				message.channel,
				":no_entry_sign: The Role: `{0}` is to high. Phaaze highest role has to be higher in hierarchy then: `{0}`".format(role.name.replace("`","´")))

		if role.managed:
			return await BASE.phaaze.send_message(
				message.channel,
				":no_entry_sign: The Role: `{0}` is managed by a integration/app (Twitch, bot... etc), Phaaze can't give this Role to others.".format(role.name.replace("`","´")))

		BASE.PhaazeDB.update(
			of="discord/server_setting",
			where=f"data['server_id'] == '{message.server.id}'",
			content=dict(autorole=role.id)
		)

		return await BASE.phaaze.send_message(message.channel, ":white_check_mark: Autorole has been set to `{0}`".format(role.name))

	async def _clear_(BASE, message, kwargs):
		BASE.PhaazeDB.update(
			of="discord/server_setting",
			where=f"data['server_id'] == '{message.server.id}'",
			content=dict(autorole=None)
		)

		return await BASE.phaaze.send_message(message.channel, ":white_check_mark: Autorole has been cleared.")

class Logs(object):

	AV = [
			# IDEA: Maybe add more? IDK... Discord Audit Logs cover also much

			'message.delete','message.edit','message.prune',
			'member.join','member.remove','member.ban','member.unban','member.update',
			'channel.create','channel.delete',
			'role.create','role.delete',
			'phaaze.custom', 'phaaze.quote'
		]

	async def Base(BASE, message, kwargs):
		m = message.content.split()

		enabled_l = ", ".join( f"`{o}`" for o in kwargs.get('server_setting',{}).get('track_options', []) )

		if len(m) == 1 and not m[0].lower() == f"{BASE.vars.PT * 3}logs-chan":
			return await BASE.phaaze.send_message(message.channel, 	f":warning: Syntax Error!\nUsage: `{BASE.vars.PT * 3}logs(-chan) [Option] [State]`\n\n"\
																	f"`[Option]` - The Log Option you want to toggle/ or the channel mention when used `{BASE.vars.PT * 3}logs-chan`\n"\
																	f"`[State]` - The new State, `on` or `off`\n\n"\
																	f":link: PhaazeDiscord-Logs configuration is a lot easier on to the PhaazeWebsite\n"\
																	f"{' '*7}Goto https://phaaze.net/discord/dashboard/{message.server.id}#logs and log-in to configure everything\n\n"\
																	f"Currently enabled options: {enabled_l}")

		if m[0].lower() == f"{BASE.vars.PT * 3}logs-chan":
			if len(m) == 1:
				chan = message.channel

			elif message.channel_mentions:
				chan = message.channel_mentions[0]

			else:
				return await BASE.phaaze.send_message(message.channel, ":warning: Please mention a channel or leave it blank to use this one.")

			BASE.PhaazeDB.update(
				of="discord/server_setting",
				where=f"data['server_id'] == '{message.server.id}'",
				content=dict(track_channel=chan.id)
			)

			return await BASE.phaaze.send_message(message.channel, f":white_check_mark: Log channel has been set to {chan.mention} - all events will appear there.")
		else:
			if not m[1].lower() in Logs.AV:
				return await BASE.phaaze.send_message(message.channel, f":warning: {m[1]} is not a valid option - available:\n\n"+'\n'.join(o for o in Logs.AV))

			if len(m) < 3 or not m[2].lower() in ['enable','on', 'off','disable']:
				return await BASE.phaaze.send_message(message.channel, ":warning: Please use a valid state (`on` | `off`)")

			return await Logs.set_state(BASE, message, kwargs, m[1].lower(), m[2].lower())

	async def set_state(BASE, message, kwargs, option, state):
		if state.lower() in ['on', 'enable']: s = True
		elif state.lower() in ['off', 'disable']: s = False
		else:
			return await BASE.phaaze.send_message(message.channel, ":warning: Please use a valid state (`on` | `off`)")

		if s and option.lower() in kwargs.get('server_setting',{}).get('track_options', []):
			return await BASE.phaaze.send_message(message.channel, f":warning: Log Option: `{option}` aleady is active.")

		elif not s and not option.lower() in kwargs.get('server_setting',{}).get('track_options', []):
			return await BASE.phaaze.send_message(message.channel, f":warning: Log Option: `{option}` aleady is disabled.")


		settings = kwargs.get('server_setting',{}).get('track_options', [])
		if s:
			settings.append(option.lower())
		else:
			settings.remove(option.lower())

		BASE.PhaazeDB.update(
			of="discord/server_setting",
			where=f"data['server_id'] == '{message.server.id}'",
			content=dict(track_options=settings)
		)

		return await BASE.phaaze.send_message(message.channel, f":white_check_mark: Log Option: `{option}` has been {'enabled'if s else 'diabled'}.")

class Everything(object):

	async def news(BASE, message, kwargs):
		# TODO: add channel to PhaazeDB?
		await BASE.phaaze.send_message(message.channel, ":x: Soon")
