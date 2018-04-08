#BASE.moduls._Discord_.PROCESS.Mod

import asyncio, json, discord, tabulate

class Settings(object):
	async def Base(BASE, message, kwargs):
		available = ["nsfw", "custom", "level", "quotes", "ai", "nonmod", "game"]
		m = message.content.lower().split()

		if len(m) == 1:
			return await BASE.phaaze.send_message(
				message.channel,
				":warning: Missing option! Available are: {0}".format(", ".join("`"+l+"`" for l in available)))

		elif m[1] == "ai":
			await Settings.ai(BASE, message, kwargs)

		if m[1] == "nsfw":
			await Settings.nsfw(BASE, message, kwargs)

		elif m[1] == "game" and "" == "-": #TODO:
			await Settings.game(BASE, message, kwargs)

		elif m[1] == "nonmod":
			await Settings.nonmod(BASE, message, kwargs)

		elif m[1] == "level":
			await Settings.level(BASE, message, kwargs)

		elif m[1] == "custom":
			await Settings.custom(BASE, message, kwargs)

		elif m[1] == "quotes":
			await Settings.quotes(BASE, message, kwargs)

		else:
			av = ", ".join("`"+l+"`" for l in available)
			return await BASE.phaaze.send_message(message.channel, f":warning: `{m[1]}` is not a option! Available are: {av}")

	async def nsfw(BASE, message, kwargs):
		m = message.content.lower().split()

		if len(m) == 2:
			return await BASE.phaaze.send_message(message.channel, f":warning: `{m[0]} {m[1]}` is missing a valid state,\nTry: `on`/`off`")

		if m[2] in ['on', 'enable', 'yes']:
			state = True

		elif m[2] in ['off', 'disable', 'no']:
			state = False

		else:
			return await BASE.phaaze.send_message(message.channel, f":warning: `{m[0]} {m[1]}` is missing a valid state,\nTry: `on`/`off`")

		server_setting = kwargs.get('server_setting', {})
		channel_list = server_setting.get('enable_chan_nsfw', [])

		if message.channel.id in channel_list and state:
			return await BASE.phaaze.send_message(message.channel, f":warning: {message.channel.mention} already has enabled NSFW")

		if message.channel.id not in channel_list and not state:
			return await BASE.phaaze.send_message(message.channel, f":warning: Can't disable NSFW for {message.channel.mention}, it's already off.")

		if state:
			channel_list.append(message.channel.id)
		else:
			channel_list.remove(message.channel.id)

		BASE.PhaazeDB.update(
			of = "discord/server_setting",
			where = f"data['server_id'] == '{message.server.id}'",
			content = dict(enable_chan_nsfw=channel_list)
		)
		state = "**disabled** :red_circle:" if not state else "**enabled** :large_blue_circle:"
		return await BASE.phaaze.send_message(message.channel, f":white_check_mark: NSFW Commands are now {state} in {message.channel.mention}")

	async def ai(BASE, message, kwargs):
		m = message.content.lower().split()

		if len(m) == 2:
			return await BASE.phaaze.send_message(message.channel, f":warning: `{m[0]} {m[1]}` is missing a valid state,\nTry: `on`/`off`")

		if m[2] in ['on', 'enable', 'yes']:
			state = True

		elif m[2] in ['off', 'disable', 'no']:
			state = False

		else:
			return await BASE.phaaze.send_message(message.channel, f":warning: `{m[0]} {m[1]}` is missing a valid state,\nTry: `on`/`off`")

		server_setting = kwargs.get('server_setting', {})
		channel_list = server_setting.get('enable_chan_ai', [])

		if message.channel.id in channel_list and state:
			return await BASE.phaaze.send_message(message.channel, f":warning: {message.channel.mention} already has enabled AI Talks")

		if message.channel.id not in channel_list and not state:
			return await BASE.phaaze.send_message(message.channel, f":warning: Can't disable AI Talks for {message.channel.mention}, it's already off.")

		if state:
			channel_list.append(message.channel.id)
		else:
			channel_list.remove(message.channel.id)

		BASE.PhaazeDB.update(
			of = "discord/server_setting",
			where = f"data['server_id'] == '{message.server.id}'",
			content = dict(enable_chan_ai=channel_list)
		)
		state = "**disabled** :red_circle:" if not state else "**enabled** :large_blue_circle:"
		return await BASE.phaaze.send_message(message.channel, f":white_check_mark: AI Talks Commands are now {state} in {message.channel.mention}")

	async def custom(BASE, message, kwargs):
		m = message.content.lower().split()

		if len(m) == 2:
			return await BASE.phaaze.send_message(message.channel, f":warning: `{m[0]} {m[1]}` is missing a valid state,\nTry: `on`/`off`")

		if m[2] in ['on', 'enable', 'yes']:
			state = True

		elif m[2] in ['off', 'disable', 'no']:
			state = False

		else:
			return await BASE.phaaze.send_message(message.channel, f":warning: `{m[0]} {m[1]}` is missing a valid state,\nTry: `on`/`off`")

		server_setting = kwargs.get('server_setting', {})
		channel_list = server_setting.get('disable_chan_custom', [])

		if message.channel.id not in channel_list and state:
			return await BASE.phaaze.send_message(message.channel, f":warning: {message.channel.mention} already allowes Custom commands")

		if message.channel.id in channel_list and not state:
			return await BASE.phaaze.send_message(message.channel, f":warning: Can't disable Custom commands in {message.channel.mention}, it's already disabled.")

		if not state:
			channel_list.append(message.channel.id)
		else:
			channel_list.remove(message.channel.id)

		BASE.PhaazeDB.update(
			of = "discord/server_setting",
			where = f"data['server_id'] == '{message.server.id}'",
			content = dict(disable_chan_custom=channel_list)
		)
		state = "**disabled** :red_circle:" if not state else "**enabled** :large_blue_circle:"
		return await BASE.phaaze.send_message(message.channel, f":white_check_mark: Custom commands are now {state} in {message.channel.mention}")

	async def quotes(BASE, message, kwargs):
		m = message.content.lower().split()

		if len(m) == 2:
			return await BASE.phaaze.send_message(message.channel, f":warning: `{m[0]} {m[1]}` is missing a valid state,\nTry: `on`/`off`")

		if m[2] in ['on', 'enable', 'yes']:
			state = True

		elif m[2] in ['off', 'disable', 'no']:
			state = False

		else:
			return await BASE.phaaze.send_message(message.channel, f":warning: `{m[0]} {m[1]}` is missing a valid state,\nTry: `on`/`off`")

		server_setting = kwargs.get('server_setting', {})
		channel_list = server_setting.get('disable_chan_quotes', [])

		if message.channel.id not in channel_list and state:
			return await BASE.phaaze.send_message(message.channel, f":warning: {message.channel.mention} already allowes Quote commands")

		if message.channel.id in channel_list and not state:
			return await BASE.phaaze.send_message(message.channel, f":warning: Can't disable Quote commands in {message.channel.mention}, it's already disabled.")

		if not state:
			channel_list.append(message.channel.id)
		else:
			channel_list.remove(message.channel.id)

		BASE.PhaazeDB.update(
			of = "discord/server_setting",
			where = f"data['server_id'] == '{message.server.id}'",
			content = dict(disable_chan_quotes=channel_list)
		)
		state = "**disabled** :red_circle:" if not state else "**enabled** :large_blue_circle:"
		return await BASE.phaaze.send_message(message.channel, f":white_check_mark: Quote commands are now {state} in {message.channel.mention}")

	async def level(BASE, message, kwargs):
		m = message.content.lower().split()

		if len(m) == 2:
			return await BASE.phaaze.send_message(message.channel, f":warning: `{m[0]} {m[1]}` is missing a valid state,\nTry: `on`/`off`")

		if m[2] in ['on', 'enable', 'yes']:
			state = True

		elif m[2] in ['off', 'disable', 'no']:
			state = False

		else:
			return await BASE.phaaze.send_message(message.channel, f":warning: `{m[0]} {m[1]}` is missing a valid state,\nTry: `on`/`off`")

		server_setting = kwargs.get('server_setting', {})
		channel_list = server_setting.get('disable_chan_level', [])

		if message.channel.id not in channel_list and state:
			return await BASE.phaaze.send_message(message.channel, f":warning: {message.channel.mention} already has enabled Level System")

		if message.channel.id in channel_list and not state:
			return await BASE.phaaze.send_message(message.channel, f":warning: Can't disable Level system in {message.channel.mention}, it's already disabled.")

		if not state:
			channel_list.append(message.channel.id)
		else:
			channel_list.remove(message.channel.id)

		BASE.PhaazeDB.update(
			of = "discord/server_setting",
			where = f"data['server_id'] == '{message.server.id}'",
			content = dict(disable_chan_level=channel_list)
		)
		state = "**disabled** :red_circle:" if not state else "**enabled** :large_blue_circle:"
		return await BASE.phaaze.send_message(
			message.channel,
			f":white_check_mark: Level system is now {state} in {message.channel.mention}\n"\
			f"(affects member XP gain and the use of level commands like: {BASE.vars.PT}level, {BASE.vars.PT}leaderboard, etc.)"
		)

	async def nonmod(BASE, message, kwargs):
		m = message.content.lower().split()

		if len(m) == 2:
			return await BASE.phaaze.send_message(message.channel, f":warning: `{m[0]} {m[1]}` is missing a valid state,\nTry: `on`/`off`")

		if m[2] in ['on', 'enable', 'yes']:
			state = True

		elif m[2] in ['off', 'disable', 'no']:
			state = False

		else:
			return await BASE.phaaze.send_message(message.channel, f":warning: `{m[0]} {m[1]}` is missing a valid state,\nTry: `on`/`off`")

		server_setting = kwargs.get('server_setting', {})
		channel_list = server_setting.get('disable_chan_normal', [])

		if message.channel.id not in channel_list and state:
			return await BASE.phaaze.send_message(message.channel, f":warning: {message.channel.mention} already has allowes normal commands")

		if message.channel.id in channel_list and not state:
			return await BASE.phaaze.send_message(message.channel, f":warning: Can't disable normal commands in {message.channel.mention}, it's already disabled.")

		if not state:
			channel_list.append(message.channel.id)
		else:
			channel_list.remove(message.channel.id)

		BASE.PhaazeDB.update(
			of = "discord/server_setting",
			where = f"data['server_id'] == '{message.server.id}'",
			content = dict(disable_chan_normal=channel_list)
		)
		state = "**disabled** :red_circle:" if not state else "**enabled** :large_blue_circle:"
		return await BASE.phaaze.send_message(
			message.channel,
			f":white_check_mark: All non-moderator commands are now {state} in {message.channel.mention}\n"\
			f"(Custom commands are not affected)"
		)

class Quote(object):

	quote_limit = 100

	async def Base(BASE, message, kwargs):
		m = message.content.split(" ")

		if len(m) == 1:
			r = f":warning: Syntax Error!\nUsage: `{BASE.vars.PT*2}quote [Option]`\n\n"\
				f"`get` - Get a link to all quotes\n"\
				f"`add` - Add a new quote\n"\
				f"`rem` - Remove a quote based on there id number: `{BASE.vars.PT}quote rem 69`\n"\
				f"`clear` - Remove all quotes"
			return await BASE.phaaze.send_message(message.channel, r)

		elif m[1].lower() == "get":
			return await BASE.phaaze.send_message(message.channel, f"All quotes for this server: https://phaaze.net/discord/quotes/{message.server.id}")
		elif m[1].lower() == "add":
			return await Quote.add(BASE, message, kwargs)
		elif m[1].lower() == "rem":
			return await Quote.rem(BASE, message, kwargs)
		elif m[1].lower() == "clear":
			return await Quote.clear(BASE, message, kwargs)
		else:
			return await BASE.phaaze.send_message(message.channel, f":warning: That's not an option.")

	async def add(BASE, message, kwargs):
		m = message.content.split()

		if len(m) == 2:
			return await BASE.phaaze.send_message(message.channel, f":warning: You need to define a quote to add.")

		quote = " ".join(x for x in m[2:])
		server_quotes = kwargs.get('server_quotes', {})

		if len(server_quotes) >= Quote.quote_limit:
			return await BASE.phaaze.send_message(message.channel, f":no_entry_sign: This server hit the quote limit of {Quote.quote_limit}, please remove some first.")

		i = BASE.PhaazeDB.insert(
			into=f"discord/quotes/quotes_{message.server.id}",
			content=dict(content=quote)
		)

		em = discord.Embed(description=quote, colour=0x11EE11)
		i = str(i['content']['id'])
		em.set_footer(text=f'ID: {i}')
		return await BASE.phaaze.send_message(message.channel, content=":white_check_mark: Quote added", embed=em)

	async def rem(BASE, message, kwargs):
		m = message.content.split()

		if len(m) == 2:
			return await BASE.phaaze.send_message(message.channel, f":warning: You need to define a quote ID to remove.")

		if not m[2].isdigit():
			return await BASE.phaaze.send_message(message.channel, f":warning: Please define a numeric ID")

		i = BASE.PhaazeDB.delete(
			of=f"discord/quotes/quotes_{message.server.id}",
			where=f"data['id'] == {m[2]}"
		)

		if i['hits'] != 1:
			return await BASE.phaaze.send_message(message.channel, f":warning: There is no Quote with ID {m[2]}")

		return await BASE.phaaze.send_message(message.channel, content=f":white_check_mark: Quote #{m[2]} removed")

	async def clear(BASE, message, kwargs):

		await BASE.phaaze.send_message(message.channel,':question: Remove all quotes? `y/n`')
		a = await BASE.phaaze.wait_for_message(timeout=30, author=message.author, channel=message.channel)
		if a.content.lower() != "y":
			return await BASE.phaaze.send_message(message.channel, ':warning: Canceled.')

		del_ = BASE.PhaazeDB.delete(of=f"discord/quotes/quotes_{message.server.id}")
		x = str( del_.get('hits', 'N/A') )
		return await BASE.phaaze.send_message(message.channel, f":white_check_mark: All {x} Quote deleted")

class Prune(object):
	async def prune(BASE, message, kwargs):
		me = await BASE.moduls._Discord_.Utils.return_real_me(BASE, message)
		phaaze_perms = message.channel.permissions_for(me)
		if not phaaze_perms.manage_messages:
			return await BASE.phaaze.send_message(message.channel, ":no_entry_sign: Phaaze need the `Manage messages` permissions to execute prune")

		m = message.content.split(" ")

		#nothing
		if len(m) == 1:
			return await BASE.phaaze.send_message(message.channel,
												f":warning: Syntax Error!\n"\
												f"Usage: `{BASE.vars.PT*2}prune [Option]`\n\n"\
												"`[Option]` - has to be a:\n\n"\
												"`number` - from 1 to 500\n"\
												"`@mention` - of the user you wanna prune\n"\
												"`exact name` - of the member **not nickname**\n"\
												"`ID` - of the member")

		#by mention
		if len(message.mentions) >= 1:
			if len(message.mentions) > 1:
				return await BASE.phaaze.send_message(message.channel, ":warning: You can not mention multiple members, only 1")

			return await Prune.by_mention(BASE, message, kwargs, message.mentions[0])

		#by id or ammount
		elif m[1].isdigit() and len(m) == 2:
			if len(m[1]) > 8:
				return await Prune.by_id(BASE, message, kwargs, m[1])
			else:
				return await Prune.by_number(BASE, message, kwargs, m[1])

		#by name
		else:
			return await Prune.by_name(BASE, message, kwargs, " ".join(f for f in m[1:]))

	async def by_mention(BASE, message, kwargs, user):

		def need_delete(check_message):
			del_ = False
			#remove all from mentiond user
			if check_message.author.id == user.id:
				del_ = True
			#and command writer
			if check_message.id == message.id:
				del_ = True

			return del_

		delete = await BASE.phaaze.purge_from(message.channel, limit=300, check=need_delete)

		confirm_delete = await BASE.phaaze.send_message(message.channel, ":wastebasket: Deleted the last **{0}** messages form `{1}` :pencil2:".format(str(len(delete)),user.name))
		await asyncio.sleep(5)
		return await BASE.phaaze.delete_message(confirm_delete)

	async def by_number(BASE, message, kwargs, number):
		c = int(number)

		if c == 0:
			return await BASE.phaaze.send_message(message.channel, ":white_check_mark: **0** messages got deleted. Good job you genius, you deleted nothing.")
		if c > 500:
			return await BASE.phaaze.send_message(message.channel, ":no_entry_sign: **{0}** messages are to much in one. Try making 2 small request, instead of 1 big.".format(str(c)))
		if c >= 100:
			await BASE.phaaze.send_message(message.channel, ":question: **{0}** are a lot, are you sure you wanna delete all of them?\n\ny/n".format(str(c)))

			r = await BASE.phaaze.wait_for_message(timeout=30, author=message.author, channel=message.channel)
			if r.content.lower() != "y":
				return await BASE.phaaze.send_message(message.channel, ":warning: Prune canceled.")

		delete = await BASE.phaaze.purge_from(message.channel, limit=c+1)

		confirm_delete = await BASE.phaaze.send_message(message.channel, ":wastebasket: Deleted the last **{0}** messages :pencil2:".format(str(len(delete)-1)))
		await asyncio.sleep(5)
		return await BASE.phaaze.delete_message(confirm_delete)

	async def by_id(BASE, message, kwargs, id_):

		def need_delete(check_message):
			del_ = False
			#remove all from user id
			if check_message.author.id == id_:
				del_ = True
			#and command writer
			if check_message.id == message.id:
				del_ = True

			return del_

		delete = await BASE.phaaze.purge_from(message.channel, limit=300, check=need_delete)

		if len(delete) == 0:
			return await BASE.phaaze.send_message(message.channel, ":warning: No messages are deleted, make sure the ID is from a member that typed something in the near past")

		else:
			confirm_delete = await BASE.phaaze.send_message(message.channel, ":wastebasket: Deleted the last **{0}** messages, that are matching the ID :pencil2:".format(str(len(delete))))
			await asyncio.sleep(5)
			return await BASE.phaaze.delete_message(confirm_delete)

	async def by_name(BASE, message, kwargs, name):

		def need_delete(check_message):
			del_ = False
			#remove all from user id
			if check_message.author.name == name:
				del_ = True
			#and command writer
			if check_message.id == message.id:
				del_ = True

			return del_

		delete = await BASE.phaaze.purge_from(message.channel, limit=300, check=need_delete)

		if len(delete) == 0:
			return await BASE.phaaze.send_message(message.channel, ":warning: No messages are deleted, make sure the name is correct.")
		else:
			confirm_delete = await BASE.phaaze.send_message(message.channel, ":wastebasket: Deleted the last **{0}** messages from `{1}` :pencil2:".format(str(len(delete)), name))
			await asyncio.sleep(5)
			return await BASE.phaaze.delete_message(confirm_delete)

async def serverinfo(BASE, message):
	m = message.content.split(" ")
	s = message.server
	rl = []

	#role list
	for role in sorted(s.role_hierarchy, reverse=True):
		if role.name != "@everyone":
			rl.append([role.position, role.name])

	#channels
	def channel_in_format():
		VCs = []
		TCs = []
		total = 0
		for channel in s.channels:
			total += 1
			if str(channel.type) == "text":
				TCs.append(channel)
			if str(channel.type) == "voice":
				VCs.append(channel)

		if len(VCs) != 1: VCs_s = "'s"
		else: VCs_s = ""
		if len(TCs) != 1: TCs_s = "'s"
		else: TCs_s = ""

		finished = "{0} - ({1} Text Channel{2} | {3} Voice Channel{4})".format(str(total), str(len(TCs)), TCs_s, str(len(VCs)), VCs_s)
		return finished

	#Emotes
	def formated_emotes():
		normal = []
		managed = []

		for emo in s.emojis:
			if not emo.managed:
				normal.append(emo)
			else:
				managed.append(emo)

		if len(normal) != 1: normal_ = "'s"
		else: normal_ = ""

		if len(managed) > 0:
			man = " (+ {0} managed by Twitch)".format(str(len(managed)))
		else: man = ""

		return "{0}{1}".format(str(len(normal)),man)

	main = 	"Server ID: {0}\n"\
			"Region: {1}\n"\
			"Members: {2}\n"\
			"Channels: {3}\n"\
			"Emotes: {4}\n"\
			"Owner: {5}\n"\
			"Verification Level: {6}\n"\
			"Created at: {7}\n".format	(
								s.id,											#0
								str(s.region),									#1
								str(s.member_count),							#2
								channel_in_format(),							#3
								formated_emotes(),								#4
								str(s.owner),									#5
								str(s.verification_level),						#6
								s.created_at.strftime("%d,%m,%y (%H:%M:%S)")	#7
										)

	tem = discord.Embed(
			description=main)

	if s.afk_channel != None:
		min_time = str(round(s.afk_timeout / 60))
		stuff = "{0} - Time: {1}m".format(s.afk_channel.name, min_time)
		tem.add_field(name=":alarm_clock: AFK channel:",value=stuff,inline=True)

	if len(rl) >= 1:
		tem.add_field(name=":notepad_spiral: Roles:",value="```" + tabulate.tabulate(rl, tablefmt="plain") + "```",inline=False)
	else:
		tem.add_field(name=":notepad_spiral: Roles:",value="None",inline=False)

	tem.set_author(name="{0}".format(s.name))
	if s.icon_url != "": tem.set_image(url=s.icon_url)
	tem.set_footer(text="To get all roles by id use ``{0}{0}getroles`".format(BASE.vars.PT))

	return await BASE.phaaze.send_message(message.channel, content=message.author.mention, embed=tem)

async def get_roles(BASE, message):
	r = message.server.role_hierarchy

	if len(r) == 0:
		return await BASE.phaaze.send_message(message.channel, ":warning: This server don't have any roles.")

	Ground = [["Pos:", "ID:", "Name:"],["","",""]]

	for role in sorted(r, reverse=True):
		if role.name != "@everyone":
			Ground.append([str(role.position), role.id, role.name])
		else:
			Ground.append([str(role.position), role.id, "everyone"])

	formated_text = "```" + tabulate.tabulate(Ground, tablefmt="plain")

	return await BASE.phaaze.send_message(message.channel, formated_text[:1996] + "```")

async def level_base(BASE, message):
	m = message.content.lower().split(" ")
	M = message.content.split(" ")
	file = await BASE.moduls.Utils.get_server_level_file(BASE, message.server.id)

	if file["disabled_by_owner"] == 1 and message.author != message.server.owner:
		return await BASE.phaaze.send_message(message.channel, ":no_entry_sign: The Serverowner disabled level manipulation.")

	if len(m) == 1:
		return await BASE.phaaze.send_message(message.channel,
											":warning: Syntax Error!\n"\
											"Usage: `{0}{0}level [Option]`\n\n"\
											"`[Option]` - has to be:\n\n"\
											"`exp` - e.g.: `{0}{0}level exp [@mention] [new_exp]`\n"\
											"`medal` - e.g.: `{0}{0}level medal [add/rem/clear] [@mention] [medal_name]`".format(BASE.vars.PT) )

	elif m[1] == "exp":
		try:
			member = message.mentions[0]
			if member.bot:
				return await BASE.phaaze.send_message(message.channel, ":no_entry_sign: `{}` is a Bot. Bots can't have levels".format(member.name))
			exp = int(m[3])
			user = await BASE.moduls.levels.Discord.get_user(file, member)

			if 1000000 < exp:
				return await BASE.phaaze.send_message(message.channel,
									":no_entry_sign: {0}? ... is too high, if you ever reach this normally it will be resetted to 0".format(str(exp)))

			user["exp"] = exp

			if exp != 0:
				user["edited"] = True
			else:
				user["edited"] = False

			with open("LEVELS/DISCORD/{0}.json".format(message.server.id), "w") as save:
				json.dump(file, save)
				setattr(BASE.levelfiles, "level_"+message.server.id, file)

			if exp != 0:
				return await BASE.phaaze.send_message(message.channel, ":white_check_mark: Set `{0}`'s EXP set to **{1}** and added a *[EDITED]* mark\n(Set EXP to 0 to remove the mark)".format(member.name, str(exp)))

			else:
				return await BASE.phaaze.send_message(message.channel, ":white_check_mark: Set `{0}`'s EXP reseted and remove the *[EDITED]* mark.".format(member.name))

		except:
			return await BASE.phaaze.send_message(message.channel, ":warning: You messed something up\n`{0}{0}level exp [@mention] [new_exp]`".format(BASE.vars.PT))

	elif m[1] == "medal":
		try:
			medal_name = " ".join(g for g in M[4:])
			user = message.mentions[0]
			if user.bot:
				return await BASE.phaaze.send_message(message.channel, ":no_entry_sign: `{}` is a Bot. Bots can't have medals".format(user.name))

			if m[2] == "add" and user.id in m[3]:
				await BASE.moduls.levels.Discord.add_medal(BASE, message, user=user, medal=medal_name, type="custom")
			elif m[2] == "rem" and user.id in m[3]:
				await BASE.moduls.levels.Discord.rem_medal(BASE, message, user=user, medal=medal_name, type="custom")
			elif m[2] == "clear" and user.id in m[3]:
				await BASE.moduls.levels.Discord.clear_custom(BASE, message, user=user)

			else: 0/0

		except:
			return await BASE.phaaze.send_message(message.channel, ":warning: You messed something up\n`{0}{0}level medal [add/rem/clear] [@mention] [medal_name]`".format(BASE.vars.PT))