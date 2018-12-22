##BASE.modules._Discord_.Custom

import asyncio, json

# store list of timeouted channels, so user cant spam
custom_command_cooldown = []

async def get(BASE, message, server_setting):
	if message.channel.id in custom_command_cooldown: return
	asyncio.ensure_future(cooldown(BASE, message))

	#are custom commands disabled?
	if message.channel.id in server_setting.get("disable_chan_custom",[]): return
	if server_setting.get("owner_disable_custom", False): return

	m = message.content.lower().split(" ")

	server_commands = await BASE.modules._Discord_.Utils.get_server_commands(BASE, message.server.id, trigger=m[0])

	for cmd in server_commands:
		if cmd.get("trigger", None) == m[0]:
			cmd["uses"] = cmd.get("uses", 0) + 1

			send = cmd.get("content", None)
			if send == None: return

			send = send.replace("[user-name]", message.author.name)
			send = send.replace("[user-mention]", message.author.mention)
			send = send.replace("[channel-name]", message.channel.name)
			send = send.replace("[channel-mention]", message.channel.mention)
			send = send.replace("[server-name]", message.server.name)
			send = send.replace("[member-count]", str(message.server.member_count))
			send = send.replace("[uses]", str(cmd["uses"]))

			BASE.PhaazeDB.update(
				of="discord/commands/commands_"+message.server.id,
				content=dict(uses = cmd["uses"]),
				where=f"data['trigger'] == {json.dumps( cmd['trigger']) }"
			)
			return await BASE.discord.send_message(message.channel, send)

async def add(BASE, message, kwargs):
	m = message.content[(len(BASE.vars.TRIGGER_DISCORD)*2):].split(" ")

	if len(m) <= 2:
		r = f":warning: Syntax Error!\nUsage: `{BASE.vars.TRIGGER_DISCORD*2}addcom [Trigger] [Content]`\n\n"\
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
			where=f"data['trigger'] == {json.dumps(trigger)}",
			content=dict(content=str(content))
		)
		await BASE.modules._Discord_.Discord_Events.Phaaze.custom(BASE, message.server.id, "update", trigger=trigger)
		return await BASE.discord.send_message(message.channel, f':white_check_mark: Command "`{trigger}`" has been **updated!**')

	#new
	else:
		if len(server_commands) >= BASE.limit.DISCORD_CUSTOM_COMAMNDS_AMOUNT:
			return await BASE.discord.send_message(message.channel, f":no_entry_sign: The limit of {BASE.limit.DISCORD_CUSTOM_COMAMNDS_AMOUNT} custom commands is reached, delete some first.")

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

async def rem(BASE, message, kwargs):
	m = message.content[(len(BASE.vars.TRIGGER_DISCORD)*2):].split(" ")

	if len(m) <= 1:
		r = f":warning: Syntax Error!\nUsage: `{BASE.vars.TRIGGER_DISCORD*2}delcom [trigger]` or `{BASE.vars.TRIGGER_DISCORD*2}delcom all`"
		return await BASE.discord.send_message(message.channel, r)

	found = False

	if m[1].lower() == "all":
		await BASE.discord.send_message(message.channel,':question: Remove all commands? `y/n`')
		a = await BASE.discord.wait_for_message(timeout=30, author=message.author, channel=message.channel)
		if a.content.lower() != "y":
			return await BASE.discord.send_message(message.channel, ':warning: Canceled.')

		del_ = BASE.PhaazeDB.delete(of=f"discord/commands/commands_{message.server.id}")
		x = str( del_.get('hits', 'N/A') )
		return await BASE.discord.send_message(message.channel, f':white_check_mark: All {x} command(s) removed.')

	server_commands = kwargs.get('server_commands', [])
	found = False

	for cmd in server_commands:
		if cmd.get("trigger", None) == m[1].lower():
			found = cmd.get("trigger", None)
			break

	if not found:
		return await BASE.discord.send_message(message.channel, f':warning: There is no command called: `{m[1].lower()}`')

	BASE.PhaazeDB.delete(
		of=f"discord/commands/commands_{message.server.id}",
		where=f"data['trigger'] == {json.dumps(found)}"
		)

	await BASE.modules._Discord_.Discord_Events.Phaaze.custom(BASE, message.server.id, "remove", trigger=m[1])
	return await BASE.discord.send_message(message.channel, f':white_check_mark: The command: "`{m[1].lower()}`" has been removed!')

async def get_all(BASE, message, kwargs):
	server_commands = await BASE.modules._Discord_.Utils.get_server_commands(BASE, message.server.id)

	if len(server_commands) == 0:
		return await BASE.discord.send_message(message.channel,
		":grey_exclamation: This server don't have custom commands!")

	a = "\n".join(f"- `{cmd.get('trigger', '[N/A]')}`" for cmd in server_commands)

	content = 	f"Available commands: **{str(len(server_commands))}**\n\n{a}"

	return await BASE.discord.send_message(message.channel, content)

async def cooldown(BASE, m):
	custom_command_cooldown.append(m.channel.id)
	await asyncio.sleep(BASE.limit.DISCORD_CUSTOM_COMMANDS_COOLDOWN)
	try:
		custom_command_cooldown.remove(m.channel.id)
	except:
		pass

