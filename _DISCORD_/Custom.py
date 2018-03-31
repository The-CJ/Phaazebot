##BASE.moduls._Discord_.Custom

import asyncio, os, json, Console

async def get(BASE, message, server_setting, server_commands):
	m = message.content.lower().split(" ")

	if message.channel.id in server_setting.get("disable_chan_custom",[]):
		return

	for cmd in server_commands:
		if cmd.get("trigger", None) == m[0]:
			cmd["uses"] = cmd("uses", 0) + 1

			send = cmd.get("content", None)
			if send == None: return

			send = send.replace("[user]", message.author.name)
			send = send.replace("[server]", message.server.name)
			send = send.replace("[count]", str(message.server.member_count))
			send = send.replace("[mention]", message.author.mention)
			send = send.replace("[uses]", str(cmd["uses"]))

			await BASE.phaaze.send_message(message.channel, send)
			await BASE.cooldown.CD_Custom(message)

async def add(BASE, message):
	m = message.content.split(" ")

	if len(m) <= 2:
		r = ":warning: Syntax Error!\nUsage: `{0}{0}addcom [Activator] [Respone]`\n\n"\
			"**Tokens:** (<-- This will be replaced by Stuff)\n"\
			"`[user]` - Member who triggered the command\n"\
			"`[server]` - Server the command has been triggered\n"\
			"`[count]` - Number of members the server has right now\n"\
			"`[mention]` - @ mention the member\n"\
			"`[uses]` - How many times a command has been used".format(BASE.vars.PT)
		return await BASE.phaaze.send_message(message.channel, r)

	trigger = m[1].lower()

	if len(trigger) >= 100:
		return await BASE.phaaze.send_message(message.channel, ":no_entry_sign: Trigger to long, maximum 100 characters")

	if trigger == "all":
		return await BASE.phaaze.send_message(message.channel, ":no_entry_sign: The trigger can't be `all`, try something else.")

	text = " ".join(f for f in m[2:])
	file = await BASE.moduls.Utils.get_server_file(BASE, message.server.id)

	file["commands"] = file.get("commands", [])

	sta = "created"
	found = None

	#check if there
	for com in file["commands"]:
		if com["trigger"].lower() == trigger.lower():
			sta = "updated"
			found = com

	#not found
	if found == None:

		#150 reached
		if len(file["commands"]) >= 150:
			return await limit_reached(BASE, message)

		file["commands"].append({
								"trigger":trigger.lower(),
								"uses":0,
								"text": text
								})
	#found
	else:
		found["text"] = text

	with open("SERVERFILES/{0}.json".format(message.server.id), "w") as save:
		json.dump(file, save)
		setattr(BASE.serverfiles, "server_"+message.server.id, file)

	#logs
	try: await BASE.moduls.Discord_Events.event_logs.custom_update(BASE, message, trigger, "add")
	except: pass

	await BASE.phaaze.send_message(message.channel, ':white_check_mark: Command "`{0}`" has been **{1}!**'.format(trigger, sta))

async def rem(BASE, message):
	m = message.content.split(" ")

	if len(m) <= 1:
		r = ":warning: Syntax Error!\nUsage: `{0}{0}delcom [command]` or `{0}{0}delcom all`".format(BASE.vars.PT)
		return await BASE.phaaze.send_message(message.channel, r)

	file = await BASE.moduls.Utils.get_server_file(BASE, message.server.id)

	try:
		file["commands"] = file["commands"]
	except:
		file["commands"] = []

	found = False

	if m[1].lower() == "all":
		await BASE.phaaze.send_message(message.channel,':question: Remove all commands? `y/n`')
		a = await BASE.phaaze.wait_for_message(timeout=30, author=message.author, channel=message.channel)
		if a.content == None or a.content.lower() == "n":
			return await BASE.phaaze.send_message(message.channel,
			':warning: Canceled.')

		if a.content.lower() == "y":

			file["commands"] = []
			with open("SERVERFILES/{0}.json".format(message.server.id), "w") as save:
				json.dump(file, save)
				setattr(BASE.serverfiles, "server_"+message.server.id, file)
				return await BASE.phaaze.send_message(message.channel,
				':white_check_mark: All commands removed.')

	for cmd in file["commands"]:
		if cmd["trigger"] == m[1].lower():
			file["commands"].remove(cmd)
			found = True
			break

	with open("SERVERFILES/{0}.json".format(message.server.id), "w") as save:
		json.dump(file, save)
		setattr(BASE.serverfiles, "server_"+message.server.id, file)

	if found:
		return await BASE.phaaze.send_message(message.channel,
		':white_check_mark: The command: "`{0}`" has been removed!'.format(m[1].lower()))
	else:
		return await BASE.phaaze.send_message(message.channel,
		':warning: There is not command called: "`{0}`"'.format(m[1].lower()))

async def get_all(BASE, message):
	file = await BASE.moduls.Utils.get_server_file(BASE, message.server.id)

	if len(file.get("commands", [])) == 0:
		return await BASE.phaaze.send_message(message.channel,
		":grey_exclamation: This server don't have custom commands!")

	one = "Available commands: **{}**\n\n".format(str(len( file.get("commands", []) )))

	two = "\n".join("- `"+g["trigger"]+"`" for g in file.get("commands", []))

	return await BASE.phaaze.send_message(message.channel, one + two)

async def limit_reached(BASE, message):
	await BASE.phaaze.send_message(message.channel, ":no_entry_sign: The limit of 150 custom commands is reached, delete some first.")


















#
