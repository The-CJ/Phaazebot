##BASE.modules._Twitch_.Custom

import asyncio

custom_command_limit = 150
custom_command_cooldown = []

async def get(BASE, message, **kwargs):
	m = message.content.split(' ')
	channel_setting = kwargs.get("channel_settings", {})
	channel_commands = kwargs.get("channel_commands", [])

	if message.channel_id in custom_command_cooldown: return

	#are custom commands disabled? (should always be true, else this function is not triggered, but to be sure)
	if not channel_setting.get("active_custom", False): return

	for cmd in channel_commands:
		if cmd.get("trigger", None) == m[0]:
			chann_cmd_hash = hash(message.channel_id+cmd.get("trigger", None))

			#command is in cooldown
			if chann_cmd_hash in custom_command_cooldown: return

			#add a use
			cmd["uses"] = cmd.get("uses", 0) + 1

			send = cmd.get("content", None)
			if send == None: return

			send = send.replace('{display_name}', message.display_name)
			send = send.replace('{name}', message.name)
			send = send.replace('{user_id}', message.user_id)
			await BASE.twitch.send_message(message.channel_name, send)
			BASE.PhaazeDB.update(
				of="twitch/commands/commands_"+message.channel_id,
				content=dict(uses = cmd["uses"]),
				where="data['trigger'] == '{}'".format( str(cmd['trigger']) )
			)
			cool = cmd.get("cooldown", 10)
			if await BASE.modules._Twitch_.Utils.is_Mod(BASE, message):
				cool = 0.01
			asyncio.ensure_future(cooldown( chann_cmd_hash, cool ))
			break

async def add(BASE, message, kwargs):
	m = message.content.split(" ")

	if len(m) <= 2:
		r = f":warning: Syntax Error!\nUsage: `{BASE.vars.PT}addcom [Trigger] [Content]`\n\n"\
			"`[Trigger]` - The thing that makes the command appear (Case insensitive)\n"\
			"`[Content]` - Whatever you want to show as the command content\n\n"\
			"You can use tokens in your `[Content]` that will be replaced by infos:\n"\
			"`[user-name]` - Current member name\n"\
			"`[user-mention]` - Current member @ mention\n"\
			"`[channel-name]` - Current channel name\n"\
			"`[channel-mention]` - Current channel @ mention\n"\
			"`[server-name]` - Current server name\n"\
			"`[member-count]` - Number of members on the the server\n"\
			"`[uses]` - How many times a command has been used"
		return await BASE.discord.send_message(message.channel, r)

	trigger = m[1].lower()
	server_commands = kwargs.get('server_commands', [])

	if len(trigger) >= 100:
		return await BASE.discord.send_message(message.channel, ":no_entry_sign: Trigger to long. Maximum: 100 characters")

	if trigger == "all":
		return await BASE.discord.send_message(message.channel, ":no_entry_sign: The trigger `all` is reservated, try something else.")

	#check if command exist
	found = False
	for com in server_commands:
		if com.get("trigger", None).lower() == trigger:
			found = True
			break

	#update
	if found:
		content = " ".join(f for f in m[2:])
		BASE.PhaazeDB.update(
			of=f"discord/commands/commands_{message.server.id}",
			where=f"data['trigger'] == '{trigger}'",
			content=dict(content=str(content))
		)
		await BASE.modules._Discord_.Discord_Events.Phaaze.custom(BASE, message.server.id, "update", trigger=trigger)
		return await BASE.discord.send_message(message.channel, f':white_check_mark: Command "`{trigger}`" has been **updated!**')

	#new
	else:
		if len(server_commands) >= custom_command_limit:
			return await BASE.discord.send_message(message.channel, f":no_entry_sign: The limit of {custom_command_limit} custom commands is reached, delete some first.")

		content = " ".join(f for f in m[2:])
		BASE.PhaazeDB.insert(
			into=f"discord/commands/commands_{message.server.id}",
			content=dict(
				content=str(content),
				trigger=str(trigger),
				uses=0
			)
		)
		await BASE.modules._Discord_.Discord_Events.Phaaze.custom(BASE, message.server.id, "new", trigger=trigger)
		return await BASE.discord.send_message(message.channel, f':white_check_mark: Command "`{trigger}`" has been **created!**')

async def cooldown(cidcmd_hash, timeout):
	#updated the command cooldown list
	#its filled with hash string
	custom_command_cooldown.append(cidcmd_hash)
	await asyncio.sleep(timeout)
	custom_command_cooldown.remove(cidcmd_hash)
