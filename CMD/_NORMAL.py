##BASE.cmds.NORMAL

import asyncio

async def base(BASE, message):
	#all disabled
	if await BASE.moduls.Utils.settings_check(BASE, message, "disable_normal"): return

	m = message.content.lower().split(" ")
	check = m[0][1:]

	if check.startswith("custom"):
		await BASE.moduls.Custom.get_all(BASE, message)

	if check.startswith("doujin"):
		if await BASE.moduls.Utils.settings_check(BASE, message, "enable_nsfw"):
			await BASE.moduls.Commands.doujin(BASE, message).request()
		else:
			await BASE.cmds.NORMAL.forbitten.nsfw(BASE, message)

	if check.startswith("help"):
		await BASE.moduls.Help.base(BASE, message)

	if check.startswith("phaaze"):
		await BASE.moduls.Utils.phaaze(BASE, message)
		await BASE.phaaze.send_message(message.channel, ":incoming_envelope: --> PM")

	if check.startswith("command"):
		await BASE.moduls.Commands.commands_base(BASE, message)

	if check.startswith("quote"):
		if not await BASE.moduls.Utils.settings_check(BASE, message, "quotes"):
			await BASE.moduls.Commands.quotes(BASE, message)
		else:
			await BASE.cmds.NORMAL.forbitten.quotes(BASE, message)

	if check.startswith("define"):
		await BASE.moduls.Commands.define(BASE, message)

	if check.startswith("wiki"):
		if message.author.id in BASE.cooldown.Wikipedia_cooldowns: return

		BASE.cooldown.Wikipedia_cooldowns.append(message.author.id)

		await BASE.moduls.Commands.wiki.wiki(BASE, message)

		await asyncio.sleep(15)
		BASE.cooldown.Wikipedia_cooldowns.remove(message.author.id)

	if check.startswith("whois"):
		await BASE.moduls.Commands.whois.whois(BASE, message)

	if check.startswith("level"):
		await BASE.moduls.levels.Discord.GetLevelStatus(BASE, message)

	if check.startswith("leaderboard"):
		await BASE.moduls.levels.Discord.leaderboards(BASE, message)

	if check.startswith("emotes"):
		await BASE.moduls.Commands.emotes(BASE, message)

	if check.startswith("about"):
		await BASE.moduls.Utils.about(BASE, message)

	if check.startswith("osu"):
		await BASE.moduls.Commands.osu_base(BASE, message)

	if check.startswith("choice"):
		await BASE.moduls.Commands.choice(BASE, message)

	return	#Soon TM

	if check.startswith("gamble"): #todo
		await BASE.moduls.Commands.commands_base(BASE, message)

	if check.startswith("dice"):#todo
		await BASE.moduls.Commands.commands_base(BASE, message)

	if check.startswith("credit"): #todo
		await BASE.moduls.Commands.commands_base(BASE, message)

class forbitten(object):
	async def nsfw(BASE, message):
		i = await BASE.phaaze.send_message(message.channel,
		":no_entry_sign: This Commands can only used in enabled channels\nTo enable/disable: `{0}{0}settings nsfw`".format(BASE.vars.PT))
		await asyncio.sleep(3)
		return await BASE.phaaze.delete_message(i)

	async def quotes(BASE, message):
		i = await BASE.phaaze.send_message(message.channel,
		":no_entry_sign: This Command has been disabled in this channels\nTo enable/disable: `{0}{0}settings quotes`".format(BASE.vars.PT))
		await asyncio.sleep(3)
		return await BASE.phaaze.delete_message(i)
