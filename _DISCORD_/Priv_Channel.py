##BASE.modules._Discord_.Priv

import asyncio, discord

PRIVATE_COOLDOWN = []

async def base(BASE, message):
#invite to dev
	if message.content.lower().startswith(BASE.vars.TRIGGER_DISCORD + "server"):
		await invite(BASE, message)
#join
	elif message.content.lower().startswith(BASE.vars.TRIGGER_DISCORD + "join"):
		await join(BASE, message)
#nischt
	else:
		await No_cmd(BASE, message)


async def invite(BASE, message):
	if message.author.id not in PRIVATE_COOLDOWN:
		await BASE.discord.send_message(message.author, "Hey {0} \nWanna join the Phaaze Development Server?\n the right place to report bug, made suggestions or just ask questions\nhttps://discord.gg/ZymrebS".format(message.author.name))
		await cooldown(message)

async def join(BASE, message):
	if message.author.id not in PRIVATE_COOLDOWN:
		info = await BASE.discord.application_info()
		await BASE.discord.send_message(message.channel,
		"For adding {1} to your server.\nJust click that sexy link and follow the instructions\n\n**{0}**".format(discord.utils.oauth_url(info.id, discord.Permissions(permissions=8)), info.name))
		await cooldown(message)

async def No_cmd(BASE, message):
	if message.author.id not in PRIVATE_COOLDOWN:
		await BASE.discord.send_message(message.author, ":warning: Unknown Command")
		await cooldown(message)


async def cooldown(m):
	PRIVATE_COOLDOWN.append(m.author.id)
	await asyncio.sleep(5)
	try:
		PRIVATE_COOLDOWN.remove(m.author.id)
	except:
		pass

