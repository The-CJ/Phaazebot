##BASE.modules._Discord_.Priv

import asyncio, discord

private_cooldown = []
private_commands = ["server", "join", "help"]

async def Base(BASE, message):
	if message.author.id in private_cooldown: return
	asyncio.ensure_future(cooldown(BASE, message))

	#invite to dev
	if message.content.lower().startswith(BASE.vars.TRIGGER_DISCORD + "server"):
		await invite(BASE, message)
	#join
	elif message.content.lower().startswith(BASE.vars.TRIGGER_DISCORD + "join"):
		await join(BASE, message)
	#help
	elif message.content.lower().startswith(BASE.vars.TRIGGER_DISCORD + "help"):
		await help_(BASE, message)
	#none
	else:
		await no_cmd(BASE, message)


async def invite(BASE, message):
	return await BASE.discord.send_message(
		message.author,
		f"Hey {message.author.name} \n"\
		"Wanna join the Phaaze Development Server?\n"\
		"the right place to report bug, made suggestions or just ask questions\n"\
		"https://discord.gg/ZymrebS"
	)

async def join(BASE, message):
	info = await BASE.discord.application_info()
	link = discord.utils.oauth_url(info.id, discord.Permissions(permissions=8))
	return await BASE.discord.send_message(
		message.channel,
		f"For adding {info.name} to your server.\n"\
		f"Just click that sexy link and follow the instructions\n\n**{link}**"
	)

async def help_(BASE, message):
	return await BASE.discord.send_message(
		message.author,
		"Need help with something?\n"\
		"No problem!\n"\
		f"Check out the wiki or use `{BASE.vars.TRIGGER_DISCORD}server` to get a invite in the Dev Server\n"\
		"Wiki: https://phaaze.net/wiki"
	)

async def no_cmd(BASE, message):
	v = "\n".join(c for c in private_commands)
	await BASE.discord.send_message(
		message.author,
		":warning: Unknown Command\n"\
		"Here's a list of commands Phaaze can to in a private channel, for more you need to interact with Phaaze on a server\n"\
		f"```{v}```"
	)

async def cooldown(BASE, m):
	private_cooldown.append(m.author.id)
	await asyncio.sleep(BASE.limit.DISCORD_PRIVATE_COOLDOWN)
	try:
		private_cooldown.remove(m.author.id)
	except:
		pass

