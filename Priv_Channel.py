import asyncio, discord

async def base(BASE, message):
#invite to dev
	if message.content.lower().startswith(BASE.vars.PT + "invite"):
		await invite(BASE, message)
#join
	elif message.content.lower().startswith(BASE.vars.PT + "join"):
		await join(BASE, message)
#phaaze
	elif message.content.lower().startswith(BASE.vars.PT + "phaaze"):
		await phaaze_info(BASE, message)
#comms
	elif message.content.lower().startswith(BASE.vars.PT + "command"):
		await commands_help(BASE, message)
#help
	elif message.content.lower().startswith(BASE.vars.PT + "help"):
		await BASE.moduls.Help.base(BASE,message)
#about
	elif message.content.lower().startswith(BASE.vars.PT + "about"):
		await BASE.moduls.Utils.about(BASE, message)
#nischt
	else:
		await No_comd(BASE, message)


async def invite(BASE, message):
	if message.author.id not in BASE.cooldown.Priv_CD:
		await BASE.phaaze.send_message(message.author, "Hey {0} \nWanna join the Phaaze Development Server?\n the right place to report bug, made suggestions or just ask questions\nhttps://discord.gg/ZymrebS".format(message.author.name))
		await BASE.cooldown.CD_Priv(message)

async def join(BASE, message):
	if message.author.id not in BASE.cooldown.Priv_CD:
		info = await BASE.phaaze.application_info()
		await BASE.phaaze.send_message(message.channel,
		"For adding {1} to your server.\nJust click that sexy link and follow the instructions\n\n**{0}**".format(discord.utils.oauth_url(info.id, discord.Permissions(permissions=8)), info.name))
		await BASE.cooldown.CD_Priv(message)

async def phaaze_info(BASE, message):
	if message.author.id not in BASE.cooldown.Priv_CD:
		await BASE.moduls.Utils.phaaze(BASE, message)
		await BASE.cooldown.CD_Priv(message)

async def commands_help(BASE, message):
	if message.author.id not in BASE.cooldown.Priv_CD:

		text = await BASE.moduls.Utils.get_Priv_Commands(BASE, message)

		text.set_footer(text="▶ These are only privat commands, for more type `{0}commands` in a server".format(BASE.vars.PT))
		text.set_author(name="Commands", icon_url=BASE.vars.app.icon_url)

		await BASE.phaaze.send_message(message.author, embed=text)
		await BASE.cooldown.CD_Priv(message)

async def higher_commands(BASE, message):
	if message.author.id not in BASE.cooldown.Priv_CD:
		await BASE.phaaze.send_message(message.channel,
		"To get a list of Moderator or Owner Commands, please use: `{0}commands` in a server chat".format(BASE.vars.PT))
		await BASE.cooldown.CD_Priv(message)

async def No_comd(BASE, message):
	if message.author.id not in BASE.cooldown.Priv_CD:
		await BASE.phaaze.send_message(message.author, ":warning: Unknown Command, type `{0}commands` for a list a commands".format(BASE.vars.PT))
		await BASE.cooldown.CD_Priv(message)











#
