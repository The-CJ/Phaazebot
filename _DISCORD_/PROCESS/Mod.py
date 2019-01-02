#BASE.modules._Discord_.PROCESS.Mod

import asyncio, discord, tabulate, json, datetime

class Settings(object):
	async def Base(BASE, message, kwargs):
		AVAILABLE = ["nsfw", "custom", "level", "quotes", "ai", "nonmod", "game"]
		m = message.content[(len(BASE.vars.TRIGGER_DISCORD)*2):].lower().split()

		if len(m) == 1:
			return await BASE.discord.send_message(
				message.channel,
				":warning: Missing option! Available are: {0}".format(", ".join("`"+l+"`" for l in AVAILABLE)))

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
			av = ", ".join("`"+l+"`" for l in AVAILABLE)
			return await BASE.discord.send_message(message.channel, f":warning: `{m[1]}` is not a option! Available are: {av}")

	# # #

	async def nsfw(BASE, message, kwargs):
		m = message.content[(len(BASE.vars.TRIGGER_DISCORD)*2):].lower().split()

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
		m = message.content[(len(BASE.vars.TRIGGER_DISCORD)*2):].lower().split()

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
		m = message.content[(len(BASE.vars.TRIGGER_DISCORD)*2):].lower().split()

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
		m = message.content[(len(BASE.vars.TRIGGER_DISCORD)*2):].lower().split()

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
		m = message.content[(len(BASE.vars.TRIGGER_DISCORD)*2):].lower().split()

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
			f"(affects member XP gain and the use of level commands like: {BASE.vars.TRIGGER_DISCORD}level, {BASE.vars.TRIGGER_DISCORD}leaderboard, etc.)"
		)

	async def nonmod(BASE, message, kwargs):
		m = message.content[(len(BASE.vars.TRIGGER_DISCORD)*2):].lower().split()

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

	async def Base(BASE, message, kwargs):
		m = message.content[(len(BASE.vars.TRIGGER_DISCORD)*2):].split(" ")

		if len(m) == 1:
			r = f":warning: Syntax Error!\nUsage: `{BASE.vars.TRIGGER_DISCORD*2}quote [Option]`\n\n"\
				f"`get` - Get a link to all quotes\n"\
				f"`add` - Add a new quote\n"\
				f"`rem` - Remove a quote based on there id number: `{BASE.vars.TRIGGER_DISCORD}quote rem 69`\n"\
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
		m = message.content[(len(BASE.vars.TRIGGER_DISCORD)*2):].split()

		if len(m) == 2:
			return await BASE.discord.send_message(message.channel, f":warning: You need to define a quote to add.")

		quote = " ".join(x for x in m[2:])
		server_quotes = await BASE.modules._Discord_.Utils.get_server_quotes(BASE, message.server.id)

		if len(server_quotes) >= BASE.limit.DISCORD_QUOTES_AMOUNT:
			return await BASE.discord.send_message(message.channel, f":no_entry_sign: This server hit the quote limit of {BASE.limit.DISCORD_QUOTES_AMOUNT}, please remove some first.")

		i = BASE.PhaazeDB.insert(
			into=f"discord/quotes/quotes_{message.server.id}",
			content=dict(content=quote)
		)

		em = discord.Embed(description=quote, colour=0x11EE11)
		i = str(i['data']['id'])
		em.set_footer(text=f'ID: {i}')
		await BASE.modules._Discord_.Discord_Events.Phaaze.quote(BASE, message, "add")
		return await BASE.discord.send_message(message.channel, content=":white_check_mark: Quote added", embed=em)

	async def rem(BASE, message, kwargs):
		m = message.content[(len(BASE.vars.TRIGGER_DISCORD)*2):].split()

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

		await BASE.modules._Discord_.Discord_Events.Phaaze.quote(BASE, message, "remove")
		return await BASE.discord.send_message(message.channel, content=f":white_check_mark: Quote #{m[2]} removed")

	async def clear(BASE, message, kwargs):

		await BASE.discord.send_message(message.channel,':question: Remove all quotes? `y/n`')
		a = await BASE.discord.wait_for_message(timeout=30, author=message.author, channel=message.channel)
		if a.content.lower() != "y":
			return await BASE.discord.send_message(message.channel, ':warning: Canceled.')

		del_ = BASE.PhaazeDB.delete(of=f"discord/quotes/quotes_{message.server.id}")
		x = str( del_.get('hits', 'N/A') )
		await BASE.modules._Discord_.Discord_Events.Phaaze.quote(BASE, message, "clear")
		return await BASE.discord.send_message(message.channel, f":white_check_mark: All {x} Quote deleted")

class Prune(object):
	async def Base(BASE, message, kwargs):
		me = await BASE.modules._Discord_.Utils.return_real_me(BASE, message)
		phaaze_perms = message.channel.permissions_for(me)
		if not phaaze_perms.manage_messages:
			return await BASE.discord.send_message(message.channel, ":no_entry_sign: Phaaze need the `Manage messages` permissions to execute prune")

		m = message.content[(len(BASE.vars.TRIGGER_DISCORD)*2):].split(" ")

		try:
			#nothing -> cancle
			if len(m) == 1:
				return await BASE.discord.send_message(message.channel,
													f":warning: Syntax Error!\n"\
													f"Usage: `{BASE.vars.TRIGGER_DISCORD*2}prune [Option]`\n\n"\
													"`[Option]` - has to be a:\n\n"\
													"`number` - from 1 to 500\n"\
													"`@mention` - of the user you wanna prune\n"\
													"`exact name` - of the member **not nickname**\n"\
													"`ID` - of the member")

			#by mention
			if len(message.mentions) >= 1:
				if len(message.mentions) > 1:
					return await BASE.discord.send_message(message.channel, ":warning: You can not mention multiple members, only 1")

				return await Prune.execute(BASE, message, kwargs, method="mention", arg=message.mentions[0])

			#by id or ammount
			elif m[1].isdigit() and len(m) == 2:
				if len(m[1]) > 8:
					return await Prune.execute(BASE, message, kwargs, method="id", arg=m[1])
				else:
					return await Prune.execute(BASE, message, kwargs, method="number", arg=m[1])

			#by name
			else:
				name = " ".join(f for f in m[1:])
				return await Prune.execute(BASE, message, kwargs, method="name", arg=name)

		except:
			return await BASE.discord.send_message(
				message.channel,
				":no_entry_sign: Prune could not be executed, something went wrong, sorry")

	class Prune_Check(object):
		def __init__(self, mod_message, method, arg):
			self.mod_message = mod_message
			self.method = method
			self.arg = arg
			self.prune_date_limit = datetime.timedelta(weeks=2)
			self.message_to_old = 0

		def check(self, check_message):

			# also delete mod author message
			if check_message.id == self.mod_message.id:
				return True

			# check mention
			if self.method == "mention":
				if check_message.author.id != self.arg.id:
					return False

			# check id
			if self.method == "id":
				if check_message.author.id != self.arg:
					return False

			# check name
			if self.method == "name":
				if check_message.author.name != self.arg:
					return False

			# check date
			now = datetime.datetime.now()
			max_time_back = now - self.prune_date_limit
			if check_message.timestamp < max_time_back: # <- older 14 days from now
				self.message_to_old += 1
				return False

			return True

	async def execute(BASE, message, kwargs, method=None, arg=None):
		if method not in ["mention", "id", "number", "name"]: raise AttributeError("prune got no method")
		if arg == None: raise AttributeError("prune got no arg")

		limit = 300

		# limit
		if method == "number" and arg.isdigit():
			arg = int(arg)

			#secure ask
			if arg >= 100:
				await BASE.discord.send_message(
					message.channel,
					f":question: **{arg}** are a lot, are you sure you wanna delete all of them?\n\ny/n"
				)

				ans = await BASE.discord.wait_for_message(timeout=30, author=message.author, channel=message.channel)
				if ans.content.lower() != "y":
					return await BASE.discord.send_message(message.channel, ":warning: Prune canceled.")

			#over
			if arg > 500:
				return await BASE.discord.send_message(message.channel, f":no_entry_sign: **{arg}** messages are to much in one. Try making 2 small request, instead of one big.")

			limit = arg + 1 #+1 because the message of the moderator to prune the channel

		P = Prune.Prune_Check(message, method, arg)

		#add channel to message.delete ignore list
		BASE.modules._Discord_.Discord_Events.Message.prune_lock.append(message.channel.id)

		#the actuall prune
		delete_amount = await BASE.discord.purge_from(message.channel, limit=limit, check=P.check)

		addition_prune = ""

		if method == "name":
			addition_prune = f"\nfrom: {arg}"

		elif method == "id":
			addition_prune = f"\nfrom User with ID: {arg}"

		elif method == "mention":
			addition_prune = f"\nfrom: {arg.name}"

		if P.message_to_old > 0:
			addition_prune = addition_prune + f"\n({P.message_to_old} could not be deleted, because there are older than 14 days)"

		confirm_delete = await BASE.discord.send_message(
			message.channel,
			f":wastebasket: Deleted the last **{len(delete_amount)-1}** messages :pencil2:"\
			f"{addition_prune}"
		)
		asyncio.ensure_future( BASE.modules._Discord_.Discord_Events.Message.prune(BASE, message, len(delete_amount)-1) )
		await asyncio.sleep(10)
		return await BASE.discord.delete_message(confirm_delete)

class Level(object):
	async def Base(BASE, message, kwargs):
		m = message.content[(len(BASE.vars.TRIGGER_DISCORD)*2):].split(" ")

		if len(m) == 1:
			r = f":warning: Syntax Error!\nUsage: `{BASE.vars.TRIGGER_DISCORD*2}level [Option]`\n\n"\
				f"`exp` - Edit a users exp and level\n"\
				f"`medal` - add/rem/clear a users medals\n"\
				f"`channel` - Set or remove a channel, where all level ups get announced\n"
			return await BASE.discord.send_message(message.channel, r)

		elif m[1].lower() == "exp":
			return await Level.exp(BASE, message, kwargs)
		elif m[1].lower() == "medal":
			return await Level.medal(BASE, message, kwargs)
		elif m[1].lower() == "channel":
			return await Level.channel(BASE, message, kwargs)
		elif m[1].lower() == "message":
			return await Level.message(BASE, message, kwargs)
		else:
			return await BASE.discord.send_message(message.channel, f":warning: `{m[1]}` is not an option.")

	async def exp(BASE, message, kwargs):
		m = message.content[(len(BASE.vars.TRIGGER_DISCORD)*2):].split(" ")

		if len(m) <= 3:
			r = f":warning: Syntax Error!\nUsage: `{BASE.vars.TRIGGER_DISCORD*2}level exp [New Exp] [Member]`\n\n"\
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
		m = message.content[(len(BASE.vars.TRIGGER_DISCORD)*2):].split(" ")

		if len(m) <= 3:
			r = f":warning: Syntax Error!\nUsage: `{BASE.vars.TRIGGER_DISCORD*2}level medal [Method] [@Member] [Medalname]`\n\n"\
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

	async def channel(BASE, message, kwargs):
		m = message.content[(len(BASE.vars.TRIGGER_DISCORD)*2):].split(" ")

		server_setting = kwargs.get('server_setting', None)
		if server_setting == None:
			server_setting = await BASE.modules._Discord_.Utils.get_server_setting(BASE, message.server.id)

		current_channel = server_setting.get('level_announce_channel', None)
		current_channel = discord.utils.get(message.server.channels, id=current_channel)
		if current_channel != None:
			current_channel = current_channel.mention
		else:
			current_channel = "None"

		if len(m) <= 2:
			r = f"Current channel: {current_channel}\n"\
				f"use: `{BASE.vars.TRIGGER_DISCORD*2}level channel [#Channel]` to change\n\n"\
				f"`#Channel` - a # mention of a channel, or \"clear\" to remove"
			return await BASE.discord.send_message(message.channel, r)

		if m[2].lower() == "clear":
			BASE.PhaazeDB.update(
				of="discord/server_setting",
				where=f"data['server_id'] == '{message.server.id}'",
				content=dict(level_announce_channel=None)
			)
			return await BASE.discord.send_message(message.channel, ':white_check_mark: Level-Announce-Channel removed.')

		if len(message.channel_mentions) != 1:
			return await BASE.discord.send_message(message.channel, ':warning: You must # mention a channel.')

		chan = message.channel_mentions[0]

		BASE.PhaazeDB.update(
			of="discord/server_setting",
			where=f"data['server_id'] == '{message.server.id}'",
			content=dict(level_announce_channel=chan.id)
		)
		return await BASE.discord.send_message(message.channel, ':white_check_mark: Level-Announce-Channel set to '+chan.mention)

	async def message(BASE, message, kwargs):
		m = message.content[(len(BASE.vars.TRIGGER_DISCORD)*2):].split(" ")
		server_setting = kwargs.get('server_setting', None)

		if len(m) <= 2:
			r = f":warning: Syntax Error!\nUsage: `{BASE.vars.TRIGGER_DISCORD*2}level message [Option]`\n\n"\
				f"`Option` can be:\n"\
				f"`get`, `set` or `clear`"
			return await BASE.discord.send_message(message.channel, r)

		if m[2].lower() not in ["get", "set", "clear"]:
			return await BASE.discord.send_message(message.channel, ":warning: Thats not an option")

		if m[2].lower() == "get":
			current_message = server_setting.get("level_custom_message", None)

			if current_message == None:
				return await BASE.discord.send_message(message.channel, ":information_source: There is no custom levelup message")
			else:
				return await BASE.discord.send_message(message.channel, f"Current: ```{current_message}```")

		elif m[2].lower() == "clear":
			BASE.PhaazeDB.update(of="discord/server_setting", where=f"data['server_id'] == {json.dumps(message.server.id)}", content=dict(level_custom_message=None))
			return await BASE.discord.send_message(message.channel, ":white_check_mark: Custom levelup message removed")

		elif m[2].lower() == "set":

			if len(m) <= 3:
				return await BASE.discord.send_message(
					message.channel,
					":warning: Missing a message to set, the message can contain token, that will be replaced\n\n"\
					"`[mention]` - A @mention of the user\n"\
					"`[name]` - User name\n"\
					"`[id]` - User id\n"\
					"`[exp]` - The exp the user have right now\n"\
					"`[lvl]` - The level the user have right now"
				)

			new_message = " ".join(m[3:])
			BASE.PhaazeDB.update(of="discord/server_setting", where=f"data['server_id'] == {json.dumps(message.server.id)}", content=dict(level_custom_message=new_message))
			return await BASE.discord.send_message(message.channel, ":white_check_mark: Custom levelup message set")

class Giverole(object):

	async def Base(BASE, message, kwargs):
		m = message.content[(len(BASE.vars.TRIGGER_DISCORD)*2):].split(" ")

		if len(m) <= 2:
			r = f":warning: Syntax Error!\nUsage: `{BASE.vars.TRIGGER_DISCORD*2}giverole [add/rem] [Trigger] [Role]`\n\n"\
				f"`add/rem` - add a new rule or remove it \n"\
				f"`Trigger` - a key to identify what role sould be added/removed\n"\
				f"`Role` - a role mention, role ID or full Role name"
			return await BASE.discord.send_message(message.channel, r)

		if m[1].lower() == "add":
			return await Giverole._add_(BASE, message, kwargs)

		elif m[1].lower() == "rem":
			return await Giverole._rem_(BASE, message, kwargs)

		else:
			return await BASE.discord.send_message(message.channel, f":warning: `{m[1]}` is not available, try `{BASE.vars.TRIGGER_DISCORD * 2}giverole`")

	async def _add_(BASE, message, kwargs):
		m = message.content[(len(BASE.vars.TRIGGER_DISCORD)*2):].split(" ")

		me = await BASE.modules._Discord_.Utils.return_real_me(BASE, message)

		if not me.server_permissions.manage_roles:
			return await BASE.discord.send_message(
				message.channel,
				":no_entry_sign: Phaaze don't has a role with the `Manage Roles` Permission."
			)

		if len(m) == 3:
			return await BASE.discord.send_message(
				message.channel,
				":warning: You need to define a role to set, you can do this via a role mention, role ID or full Role name.")

		#by role mention
		if len(message.role_mentions) == 1:
			role = message.role_mentions[0]

		#by id
		elif m[3].isdigit() and len(m) <= 4:
			role = discord.utils.get(message.server.roles, id=m[3])
			if role == None:
				return await BASE.discord.send_message(
					message.channel,
					f":warning: No Role with the ID: `{m[3]}` found"
				)

		#by name
		else:
			r_n = " ".join(d for d in m[3:])
			role = discord.utils.get(message.server.roles, name=r_n)
			if role == None:
				return await BASE.discord.send_message(
					message.channel,
					f":warning: No Role with the Name: `{r_n}` found."
				)

		if me.top_role < role:
			return await BASE.discord.send_message(
				message.channel,
				":no_entry_sign: The Role: `{0}` is to high. Phaaze highest role has to be higher in hierarchy then: `{0}`".format(role.name.replace("`","´")))

		add_rolelist = await BASE.modules._Discord_.Utils.get_server_addrolelist(BASE, message.server.id)

		if len(add_rolelist) >= BASE.limit.DISCORD_ADDROLE_AMOUNT:
			return await BASE.discord.send_message(message.channel, f":no_entry_sigh: The server already reached the limit of {BASE.limit.DISCORD_ADDROLE_AMOUNT} add/take -roles")

		check_role = None
		for check_role_lit in add_rolelist:
			if check_role_lit.get('trigger', None) == m[2].lower():
				check_role = check_role_lit

		if check_role != None:
			ac = dict(role_id=role.id)
			BASE.PhaazeDB.update(of=f'discord/addrole/addrole_{message.server.id}', content=ac, where=f"data['trigger'] == {json.dumps(m[2].lower())}")
			return await BASE.discord.send_message(message.channel, f":white_check_mark: Successfull updated Giverole `{m[2]}` with role: `{role.name}`")

		else:
			ac = dict(role_id=role.id, trigger=m[2].lower())
			BASE.PhaazeDB.insert(into=f'discord/addrole/addrole_{message.server.id}', content=ac)
			return await BASE.discord.send_message(message.channel, f":white_check_mark: Successfull added Giverole `{m[2]}` with role: `{role.name}`")

	async def _rem_(BASE, message, kwargs):
		m = message.content[(len(BASE.vars.TRIGGER_DISCORD)*2):].split(" ")

		trigger = m[2]

		add_rolelist = await BASE.modules._Discord_.Utils.get_server_addrolelist(BASE, message.server.id)

		r = None
		for role in add_rolelist:
			if role.get('trigger', None) == trigger.lower():
				r = role['trigger']
				break

		if r == None:
			return await BASE.discord.send_message(message.channel, f":warning: There is not Giverole trigger: `{trigger}`")

		BASE.PhaazeDB.delete(of=f'discord/addrole/addrole_{message.server.id}', where=f"data['trigger'] == {json.dumps(r)}")
		return await BASE.discord.send_message(message.channel, f":white_check_mark: Successfull deleted Give/Take -role `{r}`")

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

			if len(managed) > 0:
				man = f" (+ {str(len(managed))} managed by Twitch)"
			else: man = ""

			return f"{str(len(normal))}{man}"

		created_at = server.created_at.strftime("%d,%m,%y (%H:%M:%S)")

		main = 	f"Server ID: {server.id}\n"\
				f"Region: {str(server.region)}\n"\
				f"Members: {str(server.member_count)}\n"\
				f"Channels: {channel_in_format()}\n"\
				f"Emotes: {formated_emotes()}\n"\
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
		tem.set_footer(text="To get all roles by id use ``{0}{0}getroles`".format(BASE.vars.TRIGGER_DISCORD))

		return await BASE.discord.send_message(message.channel, embed=tem)

	async def listrole(BASE, message, kwargs):
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
