#BASE.moduls._Discord_.PROCESS.Mod

import asyncio, discord, tabulate

class Settings(object):
	async def Base(BASE, message, kwargs):
		available = ["nsfw", "custom", "level", "quotes", "ai", "nonmod", "game"]
		m = message.content.lower().split()

		if len(m) == 1:
			return await BASE.discord.send_message(
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
			return await BASE.discord.send_message(message.channel, f":warning: `{m[1]}` is not a option! Available are: {av}")

	async def nsfw(BASE, message, kwargs):
		m = message.content.lower().split()

		if len(m) == 2:
			return await BASE.discord.send_message(message.channel, f":warning: `{m[0]} {m[1]}` is missing a valid state,\nTry: `on`/`off`")

		if m[2] in ['on', 'enable', 'yes']:
			state = True

		elif m[2] in ['off', 'disable', 'no']:
			state = False

		else:
			return await BASE.discord.send_message(message.channel, f":warning: `{m[0]} {m[1]}` is missing a valid state,\nTry: `on`/`off`")

		server_setting = kwargs.get('server_setting', {})
		channel_list = server_setting.get('enable_chan_nsfw', [])

		if message.channel.id in channel_list and state:
			return await BASE.discord.send_message(message.channel, f":warning: {message.channel.mention} already has enabled NSFW")

		if message.channel.id not in channel_list and not state:
			return await BASE.discord.send_message(message.channel, f":warning: Can't disable NSFW for {message.channel.mention}, it's already off.")

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
		return await BASE.discord.send_message(message.channel, f":white_check_mark: NSFW Commands are now {state} in {message.channel.mention}")

	async def ai(BASE, message, kwargs):
		m = message.content.lower().split()

		if len(m) == 2:
			return await BASE.discord.send_message(message.channel, f":warning: `{m[0]} {m[1]}` is missing a valid state,\nTry: `on`/`off`")

		if m[2] in ['on', 'enable', 'yes']:
			state = True

		elif m[2] in ['off', 'disable', 'no']:
			state = False

		else:
			return await BASE.discord.send_message(message.channel, f":warning: `{m[0]} {m[1]}` is missing a valid state,\nTry: `on`/`off`")

		server_setting = kwargs.get('server_setting', {})
		channel_list = server_setting.get('enable_chan_ai', [])

		if message.channel.id in channel_list and state:
			return await BASE.discord.send_message(message.channel, f":warning: {message.channel.mention} already has enabled AI Talks")

		if message.channel.id not in channel_list and not state:
			return await BASE.discord.send_message(message.channel, f":warning: Can't disable AI Talks for {message.channel.mention}, it's already off.")

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
		return await BASE.discord.send_message(message.channel, f":white_check_mark: AI Talks Commands are now {state} in {message.channel.mention}")

	async def custom(BASE, message, kwargs):
		m = message.content.lower().split()

		if len(m) == 2:
			return await BASE.discord.send_message(message.channel, f":warning: `{m[0]} {m[1]}` is missing a valid state,\nTry: `on`/`off`")

		if m[2] in ['on', 'enable', 'yes']:
			state = True

		elif m[2] in ['off', 'disable', 'no']:
			state = False

		else:
			return await BASE.discord.send_message(message.channel, f":warning: `{m[0]} {m[1]}` is missing a valid state,\nTry: `on`/`off`")

		server_setting = kwargs.get('server_setting', {})
		channel_list = server_setting.get('disable_chan_custom', [])

		if message.channel.id not in channel_list and state:
			return await BASE.discord.send_message(message.channel, f":warning: {message.channel.mention} already allowes Custom commands")

		if message.channel.id in channel_list and not state:
			return await BASE.discord.send_message(message.channel, f":warning: Can't disable Custom commands in {message.channel.mention}, it's already disabled.")

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
		return await BASE.discord.send_message(message.channel, f":white_check_mark: Custom commands are now {state} in {message.channel.mention}")

	async def quotes(BASE, message, kwargs):
		m = message.content.lower().split()

		if len(m) == 2:
			return await BASE.discord.send_message(message.channel, f":warning: `{m[0]} {m[1]}` is missing a valid state,\nTry: `on`/`off`")

		if m[2] in ['on', 'enable', 'yes']:
			state = True

		elif m[2] in ['off', 'disable', 'no']:
			state = False

		else:
			return await BASE.discord.send_message(message.channel, f":warning: `{m[0]} {m[1]}` is missing a valid state,\nTry: `on`/`off`")

		server_setting = kwargs.get('server_setting', {})
		channel_list = server_setting.get('disable_chan_quotes', [])

		if message.channel.id not in channel_list and state:
			return await BASE.discord.send_message(message.channel, f":warning: {message.channel.mention} already allowes Quote commands")

		if message.channel.id in channel_list and not state:
			return await BASE.discord.send_message(message.channel, f":warning: Can't disable Quote commands in {message.channel.mention}, it's already disabled.")

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
		return await BASE.discord.send_message(message.channel, f":white_check_mark: Quote commands are now {state} in {message.channel.mention}")

	async def level(BASE, message, kwargs):
		m = message.content.lower().split()

		if len(m) == 2:
			return await BASE.discord.send_message(message.channel, f":warning: `{m[0]} {m[1]}` is missing a valid state,\nTry: `on`/`off`")

		if m[2] in ['on', 'enable', 'yes']:
			state = True

		elif m[2] in ['off', 'disable', 'no']:
			state = False

		else:
			return await BASE.discord.send_message(message.channel, f":warning: `{m[0]} {m[1]}` is missing a valid state,\nTry: `on`/`off`")

		server_setting = kwargs.get('server_setting', {})
		channel_list = server_setting.get('disable_chan_level', [])

		if message.channel.id not in channel_list and state:
			return await BASE.discord.send_message(message.channel, f":warning: {message.channel.mention} already has enabled Level System")

		if message.channel.id in channel_list and not state:
			return await BASE.discord.send_message(message.channel, f":warning: Can't disable Level system in {message.channel.mention}, it's already disabled.")

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
		return await BASE.discord.send_message(
			message.channel,
			f":white_check_mark: Level system is now {state} in {message.channel.mention}\n"\
			f"(affects member XP gain and the use of level commands like: {BASE.vars.PT}level, {BASE.vars.PT}leaderboard, etc.)"
		)

	async def nonmod(BASE, message, kwargs):
		m = message.content.lower().split()

		if len(m) == 2:
			return await BASE.discord.send_message(message.channel, f":warning: `{m[0]} {m[1]}` is missing a valid state,\nTry: `on`/`off`")

		if m[2] in ['on', 'enable', 'yes']:
			state = True

		elif m[2] in ['off', 'disable', 'no']:
			state = False

		else:
			return await BASE.discord.send_message(message.channel, f":warning: `{m[0]} {m[1]}` is missing a valid state,\nTry: `on`/`off`")

		server_setting = kwargs.get('server_setting', {})
		channel_list = server_setting.get('disable_chan_normal', [])

		if message.channel.id not in channel_list and state:
			return await BASE.discord.send_message(message.channel, f":warning: {message.channel.mention} already has allowes normal commands")

		if message.channel.id in channel_list and not state:
			return await BASE.discord.send_message(message.channel, f":warning: Can't disable normal commands in {message.channel.mention}, it's already disabled.")

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
		return await BASE.discord.send_message(
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
			return await BASE.discord.send_message(message.channel, r)

		elif m[1].lower() == "get":
			return await BASE.discord.send_message(message.channel, f"All quotes for this server: https://phaaze.net/discord/quotes/{message.server.id}")
		elif m[1].lower() == "add":
			return await Quote.add(BASE, message, kwargs)
		elif m[1].lower() == "rem":
			return await Quote.rem(BASE, message, kwargs)
		elif m[1].lower() == "clear":
			return await Quote.clear(BASE, message, kwargs)
		else:
			return await BASE.discord.send_message(message.channel, f":warning: That's not an option.")

	async def add(BASE, message, kwargs):
		m = message.content.split()

		if len(m) == 2:
			return await BASE.discord.send_message(message.channel, f":warning: You need to define a quote to add.")

		quote = " ".join(x for x in m[2:])
		server_quotes = kwargs.get('server_quotes', {})

		if len(server_quotes) >= Quote.quote_limit:
			return await BASE.discord.send_message(message.channel, f":no_entry_sign: This server hit the quote limit of {Quote.quote_limit}, please remove some first.")

		i = BASE.PhaazeDB.insert(
			into=f"discord/quotes/quotes_{message.server.id}",
			content=dict(content=quote)
		)

		em = discord.Embed(description=quote, colour=0x11EE11)
		i = str(i['content']['id'])
		em.set_footer(text=f'ID: {i}')
		await BASE.moduls._Discord_.Discord_Events.Phaaze.quote(BASE, message, "add")
		return await BASE.discord.send_message(message.channel, content=":white_check_mark: Quote added", embed=em)

	async def rem(BASE, message, kwargs):
		m = message.content.split()

		if len(m) == 2:
			return await BASE.discord.send_message(message.channel, f":warning: You need to define a quote ID to remove.")

		if not m[2].isdigit():
			return await BASE.discord.send_message(message.channel, f":warning: Please define a numeric ID")

		i = BASE.PhaazeDB.delete(
			of=f"discord/quotes/quotes_{message.server.id}",
			where=f"data['id'] == {m[2]}"
		)

		if i['hits'] != 1:
			return await BASE.discord.send_message(message.channel, f":warning: There is no Quote with ID {m[2]}")

		await BASE.moduls._Discord_.Discord_Events.Phaaze.quote(BASE, message, "remove")
		return await BASE.discord.send_message(message.channel, content=f":white_check_mark: Quote #{m[2]} removed")

	async def clear(BASE, message, kwargs):

		await BASE.discord.send_message(message.channel,':question: Remove all quotes? `y/n`')
		a = await BASE.discord.wait_for_message(timeout=30, author=message.author, channel=message.channel)
		if a.content.lower() != "y":
			return await BASE.discord.send_message(message.channel, ':warning: Canceled.')

		del_ = BASE.PhaazeDB.delete(of=f"discord/quotes/quotes_{message.server.id}")
		x = str( del_.get('hits', 'N/A') )
		await BASE.moduls._Discord_.Discord_Events.Phaaze.quote(BASE, message, "clear")
		return await BASE.discord.send_message(message.channel, f":white_check_mark: All {x} Quote deleted")

class Prune(object):
	async def Base(BASE, message, kwargs):
		me = await BASE.moduls._Discord_.Utils.return_real_me(BASE, message)
		phaaze_perms = message.channel.permissions_for(me)
		if not phaaze_perms.manage_messages:
			return await BASE.discord.send_message(message.channel, ":no_entry_sign: Phaaze need the `Manage messages` permissions to execute prune")

		m = message.content.split(" ")

		#nothing
		if len(m) == 1:
			return await BASE.discord.send_message(message.channel,
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
				return await BASE.discord.send_message(message.channel, ":warning: You can not mention multiple members, only 1")

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

		BASE.moduls._Discord_.Discord_Events.Message.prune_lock.append(message.channel.id)
		delete = await BASE.discord.purge_from(message.channel, limit=300, check=need_delete)

		await BASE.moduls._Discord_.Discord_Events.Message.prune(BASE, message, str(len(delete)))
		confirm_delete = await BASE.discord.send_message(message.channel, ":wastebasket: Deleted the last **{0}** messages form `{1}` :pencil2:".format(str(len(delete)),user.name))
		await asyncio.sleep(5)
		return await BASE.discord.delete_message(confirm_delete)

	async def by_number(BASE, message, kwargs, number):
		c = int(number)

		if c == 0:
			return await BASE.discord.send_message(message.channel, ":white_check_mark: **0** messages got deleted. Good job you genius, you deleted nothing.")
		if c > 500:
			return await BASE.discord.send_message(message.channel, ":no_entry_sign: **{0}** messages are to much in one. Try making 2 small request, instead of 1 big.".format(str(c)))
		if c >= 100:
			await BASE.discord.send_message(message.channel, ":question: **{0}** are a lot, are you sure you wanna delete all of them?\n\ny/n".format(str(c)))

			r = await BASE.discord.wait_for_message(timeout=30, author=message.author, channel=message.channel)
			if r.content.lower() != "y":
				return await BASE.discord.send_message(message.channel, ":warning: Prune canceled.")

		BASE.moduls._Discord_.Discord_Events.Message.prune_lock.append(message.channel.id)
		delete = await BASE.discord.purge_from(message.channel, limit=c+1)

		await BASE.moduls._Discord_.Discord_Events.Message.prune(BASE, message, str(len(delete)))
		confirm_delete = await BASE.discord.send_message(message.channel, ":wastebasket: Deleted the last **{0}** messages :pencil2:".format(str(len(delete)-1)))
		await asyncio.sleep(5)
		return await BASE.discord.delete_message(confirm_delete)

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

		BASE.moduls._Discord_.Discord_Events.Message.prune_lock.append(message.channel.id)
		delete = await BASE.discord.purge_from(message.channel, limit=300, check=need_delete)

		if len(delete) == 0:
			return await BASE.discord.send_message(message.channel, ":warning: No messages are deleted, make sure the ID is from a member that typed something in the near past")

		else:
			await BASE.moduls._Discord_.Discord_Events.Message.prune(BASE, message, str(len(delete)))
			confirm_delete = await BASE.discord.send_message(message.channel, ":wastebasket: Deleted the last **{0}** messages, that are matching the ID :pencil2:".format(str(len(delete))))
			await asyncio.sleep(5)
			return await BASE.discord.delete_message(confirm_delete)

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

		BASE.moduls._Discord_.Discord_Events.Message.prune_lock.append(message.channel.id)
		delete = await BASE.discord.purge_from(message.channel, limit=300, check=need_delete)

		if len(delete) == 0:
			return await BASE.discord.send_message(message.channel, ":warning: No messages are deleted, make sure the name is correct.")
		else:
			await BASE.moduls._Discord_.Discord_Events.Message.prune(BASE, message, str(len(delete)))
			confirm_delete = await BASE.discord.send_message(message.channel, ":wastebasket: Deleted the last **{0}** messages from `{1}` :pencil2:".format(str(len(delete)), name))
			await asyncio.sleep(5)
			return await BASE.discord.delete_message(confirm_delete)

class Level(object):
	async def Base(BASE, message, kwargs):
		m = message.content.split(" ")

		if len(m) == 1:
			r = f":warning: Syntax Error!\nUsage: `{BASE.vars.PT*2}level [Option]`\n\n"\
				f"`exp` - Edit a users exp and level\n"\
				f"`medal` - add/rem/clear a users medals"
			return await BASE.discord.send_message(message.channel, r)

		elif m[1].lower() == "exp":
			return await Level.exp(BASE, message, kwargs)
		elif m[1].lower() == "medal":
			return await Level.medal(BASE, message, kwargs)
		else:
			return await BASE.discord.send_message(message.channel, f":warning: `{m[1]}` is not an option.")

	async def exp(BASE, message, kwargs):
		m = message.content.split(" ")

		if len(m) <= 3:
			r = f":warning: Syntax Error!\nUsage: `{BASE.vars.PT*2}level exp [New Exp] [Member]`\n\n"\
				f"`Member` - a @ mention/id/name of the member you want to edit\n"\
				f"`New Exp` - the new exp amount\n\n"\
				f":information_source: Editing the exp in any way marks the user with a `[EDITED]` mark,\n"\
				f"         that can only be removed by setting it back to 0"
			return await BASE.discord.send_message(message.channel, r)

		exp = m[2]
		if not exp.isdigit():
			return await BASE.discord.send_message(message.channel, ':warning: `[New Exp]` must be numeric (0-9999999)')

		if len(message.mentions) > 0:
			user = message.mentions[0]
		else:
			user = None

		if user == None and m[3].isdigit():
			user = discord.utils.get(message.server.members, id=m[3])

		if user == None:
			user = discord.utils.get(message.server.members, name=" ".join(f for f in m[3:]))

		if user == None:
			return await BASE.discord.send_message(message.channel, ':warning: Could not find a valid user, please mention a user, use his ID or the full name')

		if user.bot:
			return await BASE.discord.send_message(message.channel, ':no_entry_sign: That is a bot user. Bots don\'t have a level')

		i = BASE.PhaazeDB.update(
			of=f"discord/level/level_{message.server.id}",
			where=f"data['member_id'] == '{user.id}'",
			content=dict(exp = int(exp), edited=True if int(exp) != 0 else False)
		)

		if i.get('hits', 0) != 1:
			return await BASE.discord.send_message(message.channel, ":warning: That user could not be found in the Datebase or never said anything")

		if int(exp) != 0:
			ed = "\nAdded the member a **[EDITED]** mark"
		else:
			ed = "\nRemoved the **[EDITED]** mark"

		return await BASE.discord.send_message(
			message.channel,
			f':white_check_mark: `{user.name}` exp has been set to **{str(exp)}**{ed}')

	async def medal(BASE, message, kwargs):
		m = message.content.split(" ")


		if len(m) <= 3:
			r = f":warning: Syntax Error!\nUsage: `{BASE.vars.PT*2}level medal [Method] [@Member] [Medalname]`\n\n"\
				f"`Method` - Add/Rem/Clear\n"\
				f"`@Member` - a @ mention of the member you want to edit\n"\
				f"`Medalname` - The actuall medall name"
			return await BASE.discord.send_message(message.channel, r)

		if m[2].lower() not in ["add", "rem", "clear"]:
			return await BASE.discord.send_message(message.channel, ':warning: Please use a valid method.')

		user = None
		if len(message.mentions) > 0:
			if message.mentions[0].id in m[3].lower():
				user = message.mentions[0]

		if user == None:
			return await BASE.discord.send_message(message.channel, ':warning: Please mention a user before typing the medal name')

		if user.bot:
			return await BASE.discord.send_message(message.channel, ':no_entry_sign: That is a bot user. Bots can\'have medals')

		command_medal = " ".join(d for d in m[4:])
		if command_medal == "" and m[2].lower() != 'clear':
			return await BASE.discord.send_message(message.channel, ':no_entry_sign: The Medal can\'t be empty.')

		if len(command_medal) >= 150:
			return await BASE.discord.send_message(message.channel, ':no_entry_sign: The Medal can\'t be longer than 150 characters.')

		#get user from Level
		db_user = BASE.PhaazeDB.select(
			of=f"discord/level/level_{message.server.id}",
			where=f"data['member_id'] == '{user.id}'",
		)

		if db_user.get('hits', 0) != 1:
			return await BASE.discord.send_message(message.channel, ':warning: Seems like that user could not found in the Database.')

		l_user = db_user['data'][0]

		# rem
		if m[2].lower() == "rem":
			success = False
			medals = l_user.get('medal', [])
			try:
				medals.remove(command_medal)
				success = True
			except:
				success = False

			if not success:
				return await BASE.discord.send_message(message.channel, f':warning: Seems like that user don\'t has a medal named `{command_medal}`.')
			else:
				BASE.PhaazeDB.update(
					of=f"discord/level/level_{message.server.id}",
					where=f"data['member_id'] == '{user.id}'",
					content=dict(medal=medals)
				)
				return await BASE.discord.send_message(message.channel, f':white_check_mark: `{command_medal}` has been removed from `{user.name}`.')

		#add
		elif m[2].lower() == "add":
			success = False
			medals = l_user.get('medal', [])
			if command_medal in medals:
				success = False
			else:
				success = True
				medals.append(command_medal)

			if not success:
				return await BASE.discord.send_message(message.channel, f':warning: Seems like that user has a medal named `{command_medal}`.')
			else:
				BASE.PhaazeDB.update(
					of=f"discord/level/level_{message.server.id}",
					where=f"data['member_id'] == '{user.id}'",
					content=dict(medal=medals)
				)
				return await BASE.discord.send_message(message.channel, f':white_check_mark: `{command_medal}` has been added to `{user.name}`.')

		#clear
		elif m[2].lower() == "clear":
			BASE.PhaazeDB.update(
				of=f"discord/level/level_{message.server.id}",
				where=f"data['member_id'] == '{user.id}'",
				content=dict(medal=[])
			)
			return await BASE.discord.send_message(message.channel, f':white_check_mark: All medals are removed from `{user.name}`.')

		else:
			return await BASE.discord.send_message(message.channel, f':warning: Please use a valid method.')

class Utils(object):

	async def serverinfo(BASE, message, kwargs):
		server = message.server
		rl = []

		#role list
		for role in sorted(server.role_hierarchy, reverse=True):
			if role.name != "@everyone":
				rl.append([role.position, role.name])

		#channels
		def channel_in_format():
			VCs = []
			TCs = []
			total = 0
			for channel in server.channels:
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

			for emo in server.emojis:
				if not emo.managed:
					normal.append(emo)
				else:
					managed.append(emo)

			if len(normal) != 1: plural = "'s"
			else: plural = ""

			if len(managed) > 0:
				man = f" (+ {str(len(managed))} managed by Twitch)"
			else: man = ""

			return f"{str(len(normal))}{plural}{man}"

		created_at = server.created_at.strftime("%d,%m,%y (%H:%M:%S)")

		main = 	f"Server ID: {server.id}\n"\
				f"Region: {str(server.region)}\n"\
				f"Members: {str(server.member_count)}\n"\
				f"Channels: {3}\n"\
				f"Emotes: {4}\n"\
				f"Owner: {server.owner.name}\n"\
				f"Verification Level: {str(server.verification_level)}\n"\
				f"Created at: {created_at}"

		tem = discord.Embed(description=main)

		if server.afk_channel != None:
			min_time = str(round(server.afk_timeout / 60))
			stuff = "{0} - Time: {1}m".format(server.afk_channel.name, min_time)
			tem.add_field(name=":alarm_clock: AFK channel:",value=stuff,inline=True)

		if len(rl) >= 1:
			tem.add_field(name=":notepad_spiral: Roles:",value="```" + tabulate.tabulate(rl, tablefmt="plain") + "```",inline=False)
		else:
			tem.add_field(name=":notepad_spiral: Roles:",value="None",inline=False)

		tem.set_author(name="{0}".format(server.name))
		if server.icon_url != "": tem.set_image(url=server.icon_url)
		tem.set_footer(text="To get all roles by id use ``{0}{0}getroles`".format(BASE.vars.PT))

		return await BASE.discord.send_message(message.channel, embed=tem)

	async def getroles(BASE, message, kwargs):
		r = message.server.role_hierarchy

		if len(r) == 0:
			return await BASE.discord.send_message(message.channel, ":warning: This server don't have any roles.")

		Ground = [["Pos:", "ID:", "Name:"],["","",""]]

		for role in sorted(r, reverse=True):
			if role.name != "@everyone":
				Ground.append([str(role.position), role.id, role.name])
			else:
				Ground.append([str(role.position), role.id, "everyone"])

		formated_text = "```" + tabulate.tabulate(Ground, tablefmt="plain")

		return await BASE.discord.send_message(message.channel, formated_text[:1996] + "```")
