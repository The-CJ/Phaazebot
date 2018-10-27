##BASE.modules._Twitch_.Custom

import asyncio, json

custom_command_cooldown = []

async def get(BASE, message, **kwargs):
	m = message.content.split(' ')
	channel_setting = kwargs.get("channel_settings", {})

	channel_commands = kwargs.get('channel_commands', [])

	if message.channel_id in custom_command_cooldown: return

	#are custom commands disabled? (should always be true, else this function is not triggered, but to be sure)
	if not channel_setting.get("active_custom", False): return

	for cmd in channel_commands:
		if cmd.get("trigger", None) == m[0]:

			#channel is in cooldown
			if message.channel_id in custom_command_cooldown: return

			#add a use
			cmd["uses"] = cmd.get("uses", 0) + 1

			send = cmd.get("content", None)
			if send == None: return

			send = send.replace('{display_name}', message.display_name)
			send = send.replace('{name}', message.name)
			send = send.replace('{user_id}', message.user_id)
			send = send.replace('{uses}', str(cmd.get('uses', 0)))

			await BASE.twitch.send_message(message.channel_name, send)
			BASE.PhaazeDB.update(
				of="twitch/commands/commands_"+message.channel_id,
				content=dict(uses = cmd["uses"]),
				where=f"data['trigger'] == {json.dumps(str(cmd['trigger']))}"
			)
			cool = cmd.get("cooldown", 10)
			if await BASE.modules._Twitch_.Utils.is_Mod(BASE, message):
				cool = 0.01
			asyncio.ensure_future(cooldown( message.channel_id, cool ))
			break

async def add(BASE, message, kwargs):
	m = message.content[len(BASE.vars.TRIGGER_TWITCH):].split(" ")

	if len(m) <= 2:
		r = f"Error! > {BASE.vars.TRIGGER_TWITCH}addcom [Trigger] [Content]"
		return await BASE.twitch.send_message(message.channel_name, r)

	trigger = m[1].lower()
	channel_commands = await BASE.modules._Twitch_.Utils.get_channel_commands(BASE, message.channel_id)

	if len(trigger) >= 50:
		return await BASE.twitch.send_message(message.channel_name, "Error: Trigger is to long. Maximum: 50 characters")

	#check if command exist
	found = False
	for cmd in channel_commands:
		if cmd.get("trigger", None).lower() == trigger:
			found = True
			break

	#update
	if found:
		content = " ".join(f for f in m[2:])
		BASE.PhaazeDB.update(
			of=f"twitch/commands/commands_{message.channel_id}",
			where=f"data['trigger'] == {json.dumps(trigger)}",
			content=dict(content=str(content))
		)
		return await BASE.twitch.send_message(message.channel_name, f'Command "{trigger}" has been updated!')

	#new
	else:
		if len(channel_commands) >= BASE.limit.TWITCH_CUSTOM_COMMAND_AMOUNT:
			return await BASE.twitch.send_message(message.channel_name, f"Error: The limit of {BASE.limit.TWITCH_CUSTOM_COMMAND_AMOUNT} custom commands is reached, delete some first.")

		content = " ".join(f for f in m[2:])
		BASE.PhaazeDB.insert(
			into=f"twitch/commands/commands_{message.channel_id}",
			content=dict(
				content=str(content),
				trigger=str(trigger),
				uses=0,
				cooldown=10 # <- can only be changed via web
			)
		)
		return await BASE.twitch.send_message(message.channel_name, f'Command "{trigger}" has been created!')

async def rem(BASE, message, kwargs):
	m = message.content[len(BASE.vars.TRIGGER_TWITCH):].split(" ")

	if len(m) <= 1:
		r = f"Error! > {BASE.vars.TRIGGER_TWITCH}delcom [trigger]"
		return await BASE.twitch.send_message(message.channel_name, r)

	channel_commands = await BASE.modules._Twitch_.Utils.get_channel_commands(BASE, message.channel_id)
	found = False

	for cmd in channel_commands:
		if cmd.get("trigger", None) == m[1].lower():
			found = cmd.get("trigger", None)
			break

	if found == False:
		return await BASE.twitch.send_message(message.channel_name, f'There is no command called: "{m[1].lower()}"')

	BASE.PhaazeDB.delete(
		of=f"twitch/commands/commands_{message.channel_id}",
		where=f"data['trigger'] == {json.dumps(found)}"
		)

	return await BASE.twitch.send_message(message.channel_name, f'The command: "{m[1].lower()}" has been removed!')

async def cooldown(channel_id, timeout):
	# cooldown a command, so it can't be spammed
	custom_command_cooldown.append(channel_id)
	await asyncio.sleep(timeout)
	custom_command_cooldown.remove(channel_id)
