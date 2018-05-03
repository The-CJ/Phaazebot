##BASE.moduls._Discord_.Priv

import asyncio, discord

async def base(BASE, message):
#invite to dev
	if message.content.lower().startswith(BASE.vars.PT + "server"):
		await invite(BASE, message)
#join
	elif message.content.lower().startswith(BASE.vars.PT + "join"):
		await join(BASE, message)
#nischt
	else:
		await No_cmd(BASE, message)


async def invite(BASE, message):
	if message.author.id not in BASE.cooldown.Priv_CD:
		await BASE.discord.send_message(message.author, "Hey {0} \nWanna join the Phaaze Development Server?\n the right place to report bug, made suggestions or just ask questions\nhttps://discord.gg/ZymrebS".format(message.author.name))
		await BASE.cooldown.CD_Priv(message)

async def join(BASE, message):
	if message.author.id not in BASE.cooldown.Priv_CD:
		info = await BASE.discord.application_info()
		await BASE.discord.send_message(message.channel,
		"For adding {1} to your server.\nJust click that sexy link and follow the instructions\n\n**{0}**".format(discord.utils.oauth_url(info.id, discord.Permissions(permissions=8)), info.name))
		await BASE.cooldown.CD_Priv(message)

async def No_cmd(BASE, message):
	if message.author.id not in BASE.cooldown.Priv_CD:
		await BASE.discord.send_message(message.author, ":warning: Unknown Command")
		await BASE.cooldown.CD_Priv(message)

