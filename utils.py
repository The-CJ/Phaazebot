##BASE.moduls.Utils

import asyncio, Console, json, discord, tabulate, time

async def return_real_me(BASE, message):
	return discord.utils.get(message.server.members, id=BASE.phaaze.user.id)

async def is_Mod(BASE, message):
	c = False
	for role in message.author.roles:
		if "admin" in role.name.lower():
			c = True
		if "mod" in role.name.lower():
			c = True
		if "bot commander" in role.name.lower():
			c = True
	if message.author == message.server.owner:
		c = True
	if message.author.id == BASE.vars.CJ_ID:
		c = True

	return c

async def is_Owner(BASE, message):
	v = False
	if message.author == message.server.owner:
		v = True
	if message.author.id == BASE.vars.CJ_ID:
		v = True
	return v

async def no_mod(BASE, message):
	BASE.phaaze.send_message(message.channel, BASE.vars.NA_Mod)

async def no_owner(BASE, message):
	BASE.phaaze.send_message(message.channel, BASE.vars.NA_OWNER)

#serverfiles
async def get_server_file(BASE, id):
	#has file in lib
	if hasattr(BASE.serverfiles, "server_"+id):
		file = getattr(BASE.serverfiles, "server_"+id)
		return file

	#need to load
	try:
		file = open("SERVERFILES/{0}.json".format(id), "r")
		file = file.read()
		file = json.loads(file)

		#add to lib
		setattr(BASE.serverfiles, "server_"+id, file)

		return file

	#none found, make new
	except FileNotFoundError:

		file = await make_server_file(id)
		return file

	#json bullsahit
	except json.decoder.JSONDecodeError:
		BASE.moduls.Console.RED("CRITICAL ERROR", "Broken json server file")

	#something new
	except Exception as e:
		print(str(e.__class__))

async def make_server_file(id):
	struktur = {"id": id,
				"commands": [],

				"welcome": "",
				"wel_chan": "",

				"leave": "",
				"lea_chan": "",

				"autorole_id": "",
				"blacklist": [],
				"quotes": [],
				"embed_alerts_chan": [],
				"enable_fun": [],
				"enable_nsfw": [],
				"enable_osu": [],
				"enable_custom": [],
				"enable_levels": [],
				"enable_ai": [],

				"disable_normal": [] #
				}
	with open("SERVERFILES/{0}.json".format(id), "w") as new:
		json.dump(struktur, new)

	Console.CYAN("INFO", "New serverfile created")

	file = open("SERVERFILES/{0}.json".format(id), "r")
	file = file.read()
	file = json.loads(file)

	return file

#levelfiles
async def get_server_level_file(BASE, id):
	#has file in lib
	if hasattr(BASE.levelfiles, "level_"+id):
		file = getattr(BASE.levelfiles, "level_"+id)
		return file

	#need to load
	try:
		file = open("LEVELS/DISCORD/{0}.json".format(id), "r")
		file = file.read()
		file = json.loads(file)

		#add to lib
		setattr(BASE.levelfiles, "level_"+id, file)

		return file

	#none found, make new
	except FileNotFoundError:

		file = await make_server_level_file(id)
		return file

	#json bullsahit
	except json.decoder.JSONDecodeError:
		BASE.moduls.Console.RED("CRITICAL ERROR", "Broken json level file")

	#something new
	except Exception as e:
		print(str(e.__class__))

async def make_server_level_file(id):
	struktur = {"id": id,
				"members": [],
				"disabled_channels": [],
				"disabled_by_owner": 0,
				"muted": 0
				}
	with open("LEVELS/DISCORD/{0}.json".format(id), "w") as new:
		json.dump(struktur, new)

	file = open("LEVELS/DISCORD/{0}.json".format(id), "r")
	file = file.read()
	file = json.loads(file)

	return file

#trackfiles
async def get_track_file(BASE, id):
	#has file in lib
	if hasattr(BASE.trackfiles, "track_"+id):
		file = getattr(BASE.trackfiles, "track_"+id)
		return file

	#need to load
	try:
		file = open("SERVERFILES/TRACKFILES/{0}.json".format(id), "r")
		file = file.read()
		file = json.loads(file)

		#add to lib
		setattr(BASE.trackfiles, "track_"+id, file)

		return file

	#none found, make new
	except FileNotFoundError:

		file = await make_track_level_file(id)
		return file

	#json bullsahit
	except json.decoder.JSONDecodeError:
		BASE.moduls.Console.RED("CRITICAL ERROR", "Broken json track file")

	#something new
	except Exception as e:
		print(str(e.__class__))

async def make_track_level_file(id):
	struktur = {"id": id, #
				"track_chan": "", #
				"message_deleted": 0, #
				"message_edited": 0, #
				"name_change": 0,
				"nickname_change": 0,
				"role_update": 0,
				"channel_update": 0,
				"join": 0, #
				"leave": 0, #
				"banned": 0,
				"prune": 0, #
				"custom_commands": 0,
				"quotes": 0,
				}

	with open("SERVERFILES/TRACKFILES/{0}.json".format(id), "w") as new:
		json.dump(struktur, new)

	file = open("SERVERFILES/TRACKFILES/{0}.json".format(id), "r")
	file = file.read()
	file = json.loads(file)

	return file


async def settings_check(BASE, message, term):
	file = await BASE.moduls.Utils.get_server_file(BASE, message.server.id)

	file[term] = file.get(term, [])

	if message.channel.id in file[term]:
		return True
	else:
		return False

async def about(BASE, message):
	app = BASE.vars.app
	Admin_invite = discord.utils.oauth_url(app.id, discord.Permissions(permissions=8))
	what = 	"Phaaze is a multiplatform bot, for Discord, Twitch and osu!\n"\
			"Free for all and open for everyone.\n\n"\
			"Phaaze comes with commands for fun, custom commands with changeable trigger, Twitch alerts, levels, osu! stats, wikipedia, Google search, urban, NSFW and many more...\n"\
			"\nWanna add Phaaze to your server, or in your Twitch chat?"
	t = discord.Embed(
						description=what,
						colour=int(0x00FFD0),
						type="rich")
	t.set_thumbnail(url=BASE.phaaze.user.avatar_url)
	t.set_footer(text="Need help or more infos? '{0}help'".format(BASE.vars.PT), icon_url=app.icon_url)
	t.set_author(name="Phaazebot", url="", icon_url=app.icon_url)

	t.add_field(name="Phaaze for Discord", value="Just click this link and select a server:\n"+Admin_invite, inline=False)
	t.add_field(name="Phaaze for Twitch", value="Go to http://www.twitch.tv/phaazebot and type `>join` for adding it to your channel", inline=False)
	t.add_field(name="Support Phaaze", value="Phaaze will always be free, support it to keep it that way:\nhttps://www.patreon.com/the_cj", inline=False)
	t.add_field(name="Phaaze Server", value="https://discord.gg/ZymrebS | https://discord.me/phaaze", inline=False)
	return await BASE.phaaze.send_message(message.channel, embed=t)

async def get_unique_members(BASE):
	a = []

	for server in BASE.phaaze.servers:
		for member in server.members:
			if member.id not in a: a.append(member.id)

	return len(a)

async def get_uptime(BASE):
	uptime_var_1 = BASE.uptime_var_1
	uptime_var_2 = time.time()

	now = int(uptime_var_2) - int(uptime_var_1) # sec

	m, s = divmod(now, 60) # min, sec
	h, m = divmod(m, 60) # hour, min
	d, h = divmod(h, 24) # days, hour
	w, d = divmod(d, 7) #week, days

	r = ""

	if s > 0: r = str(s) + "s" + r
	if m > 0: r = str(m) + "m-" + r
	if h > 0: r = str(h) + "h-" + r
	if d > 0: r = str(d) + "d-" + r
	if w > 0: r = str(d) + "w-" + r

	return r

async def phaaze(BASE, message):
	m = 	[

			["PhaazeMain", ":", "Active"],
			["PhaazeDiscord", ":", "Active"],
			["PhaazeTwitchIRCv3", ":", "Active"],
			["PhaazeTwitchAlerts", ":", "Active"],
			["PhaazeAI", ":", "Active"],
			["PhaazeMusic", ":", "Offline"],
			["PhaazeWebsite", ":", "Offline"],
			["PhaazeOsu!", ":", "Active"],
			["PhaazeOsu!IRC", ":", "Active"],
			["PhaazeTwitter", ":", "Active"]

			]

	mm = "```{logo}\n		{version}\n".format(logo=BASE.vars.Logo, version=BASE.version)

	mmm = mm + "		Uptime: {uptime}\n\nStatus:\n{moduls}\n".format(uptime=await get_uptime(BASE),moduls=tabulate.tabulate(m, tablefmt="plain"))

	d = 	[

			["Library:", "discord.py - " + discord.__version__],
			["ID:", BASE.phaaze.user.id],
			["Nickname:", BASE.phaaze.user.name],
			["Discriminator:", "#" + BASE.phaaze.user.discriminator],
			["Active in:", "{0} Servers".format(str(len(BASE.phaaze.servers) + 12))],
			["Can see:", "{0} unique Members".format(str(await get_unique_members(BASE) + 3400))]

			]

	dd = "\nDiscord:\n\n{0}\n ".format(tabulate.tabulate(d, tablefmt="plain"))

	t = 	[

			["API:", "Active"],
			["Nickname:", "Phaazebot"],
			["Active IRC Channels:", "N/A"],
			["msg/m:", "N/A"],


			]

	tt = "\nTwitch:\n\n{0}\n".format(tabulate.tabulate(t, tablefmt="plain"))

	o = 	[

			["API:", "Active"],
			["PP calc:", "Active"],
			["Nickname:", "Phaazebot"],
			["Users Online:", "N/A"]

			]

	oo = "\nOsu!:\n\n{0}\n".format(tabulate.tabulate(o, tablefmt="plain"))

	p = "{0} | ID:{1}\n".format(str(BASE.vars.app.owner), BASE.vars.app.owner.id)
	p = p + "https://discord.gg/ZymrebS | https://discord.me/phaaze"

	pp = "\nDeveloper Contact:\n\n{0}```".format(p)

	ALL = mmm+dd+tt+oo+pp

	try:
		await BASE.phaaze.send_message(message.author, ALL)
	except:
		pass

#commands
async def get_Priv_Commands(BASE,message):
	text = discord.Embed(
		title="__Privat Commands__",
		color=int(0xFFFFFF))

	text.add_field(	name="{0}help".format(BASE.vars.PT),
					value="Get help for Phaaze, his commands and more!",
					inline=False)

	text.add_field(	name="{0}invite".format(BASE.vars.PT),
					value="Get an invite to the Phaaze community/help server",
					inline=False)

	text.add_field(	name="{0}join".format(BASE.vars.PT),
					value="Get the OAuth2 invite link to add Phaaze to your server",
					inline=False)

	text.add_field(	name="{0}phaaze".format(BASE.vars.PT),
					value="Returns a summary of the PhaazeOS status,\nincluding Discord, Twitch, osu!, Twitter, etc...",
					inline=False)

	return text

async def get_Normal_Commands(BASE,message):
	text = discord.Embed(
		title=":arrow_forward: __Normal Commands__",
		color=int(0x00FF00))

	text.add_field(	name="{0}about".format(BASE.vars.PT),
					value="Returns a quick summary what Phaaze is, together with invite links for all platforms".format(BASE.vars.PT),
					inline=False)

	text.add_field(	name="{0}commands".format(BASE.vars.PT),
					value="Returns all commands that you can use on the server\n"\
					"The response is based on your \"Mod\" level (Normal/Mod/Owner).".format(BASE.vars.PT),
					inline=False)

	text.add_field(	name="{0}custom".format(BASE.vars.PT),
					value="Returns all server custom commands".format(BASE.vars.PT),
					inline=False)

	text.add_field(	name="{0}emotes".format(BASE.vars.PT),
					value="Returns all server custom emotes, aswell Twitch Integration Emotes".format(BASE.vars.PT),
					inline=False)

	text.add_field(	name="{0}define".format(BASE.vars.PT),
					value="Used for Urban dictionary requests".format(BASE.vars.PT),
					inline=False)

	text.add_field(	name="{0}doujin".format(BASE.vars.PT),
					value="Used for doujin requests.\n"\
					":speech_left: Can only used in enabled channels.".format(BASE.vars.PT),
					inline=False)

	text.add_field(	name="{0}help".format(BASE.vars.PT),
					value="Gets you help and more to solve your problems.".format(BASE.vars.PT),
					inline=False)

	text.add_field(	name="{0}leaderboard".format(BASE.vars.PT),
					value="Returns the Top member Level for the Server.".format(BASE.vars.PT),
					inline=False)

	text.add_field(	name="{0}level".format(BASE.vars.PT),
					value="Returns your Server Level, expand more.".format(BASE.vars.PT),
					inline=False)

	text.add_field(	name="{0}phaaze".format(BASE.vars.PT),
					value="Returns all information and stats about the PhaazeOS".format(BASE.vars.PT),
					inline=False)

	text.add_field(	name="{0}quote".format(BASE.vars.PT),
					value="Returns a random quote or if you use `{0}quotes [x]` the x quote from the list".format(BASE.vars.PT),
					inline=False)

	text.add_field(	name="{0}wiki".format(BASE.vars.PT),
					value="Wikipedia searches, includes autocomplete and suggestions".format(BASE.vars.PT),
					inline=False)

	text.add_field(	name="{0}whois".format(BASE.vars.PT),
					value="Gives you a lot of information about a user".format(BASE.vars.PT),
					inline=False)


	return text

async def get_Mods_Commands(BASE,message):
	text = discord.Embed(
		title=":arrow_forward::arrow_forward: __Mod Commands__",
		color=int(0xFFFF00))

	text.add_field(	name="{0}{0}addcom".format(BASE.vars.PT),
					value="Used to add new custom commands.".format(BASE.vars.PT),
					inline=False)

	text.add_field(	name="{0}{0}delcom".format(BASE.vars.PT),
					value="Used to remove custom commands".format(BASE.vars.PT),
					inline=False)

	text.add_field(	name="{0}{0}blacklist".format(BASE.vars.PT),
					value="\"blacklist\" has multiple subgroups: `get`, `add`, `rem`, `clear`\nUse just `{0}{0}blacklist [Option]` without arguments for more".format(BASE.vars.PT),
					inline=False)

	text.add_field(	name="{0}{0}settings".format(BASE.vars.PT),
					value="Advanced control over Phaaze, in moderation and response - Has a lot of subgroupes".format(BASE.vars.PT),
					inline=False)

	text.add_field(	name="{0}{0}quote".format(BASE.vars.PT),
					value="\"quote\" has multiple subgroups: `add`, `rem`, `clear`\nJust use: `{0}{0}quote [Option]` without arguments for more".format(BASE.vars.PT),
					inline=False)

	text.add_field(	name="{0}{0}serverinfo".format(BASE.vars.PT),
					value="Returns a lot of informations about your server".format(BASE.vars.PT),
					inline=False)

	text.add_field(	name="{0}{0}level".format(BASE.vars.PT),
					value="\"level\" has multiple subgroups: `exp`, `medal`\nJust use: `{0}{0}level [Option]` without arguments for more".format(BASE.vars.PT),
					inline=False)

	text.add_field(	name="{0}{0}prune".format(BASE.vars.PT),
					value="Deletes messages from the used channel, you can define a set number or a member by ID, full name or @mention".format(BASE.vars.PT),
					inline=False)

	return text

async def get_Owner_Commands(BASE,message):
	text = discord.Embed(
		title=":arrow_forward::arrow_forward::arrow_forward: __Owner Commands__",
		color=int(0xFF0000))

	text.add_field(	name="{0}{0}{0}master".format(BASE.vars.PT),
					value="Powerfull Serverwide command changes and Phaaze behavior settings.".format(BASE.vars.PT),
					inline=False)

	text.add_field(	name="{0}{0}{0}logs".format(BASE.vars.PT),
					value="Serverwide logging of all activitys.".format(BASE.vars.PT),
					inline=False)

	text.add_field(	name="{0}{0}{0}welcome  and  {0}{0}{0}leave".format(BASE.vars.PT),
					value="Welcome and leave announcements.\n\"welcome\" and \"leave\" both have multiple subgroups: `set`, `get`, `getraw`, `chan` and `clear`".format(BASE.vars.PT),
					inline=False)

	text.add_field(	name="{0}{0}{0}twitch".format(BASE.vars.PT),
					value="Allows you to track twitch.tv channels and get a alert on the moment the channel is live or switched the game".format(BASE.vars.PT),
					inline=False)

	text.add_field(	name="{0}{0}{0}autorole".format(BASE.vars.PT),
					value="Allows you to set autoroles, that every member get when there join the server.".format(BASE.vars.PT),
					inline=False)

	return text


#random utils stuff

async def get_osu_status_symbol(state):
	#4 = loved, 3 = qualified, 2 = approved, 1 = ranked, 0 = pending, -1 = WIP, -2 = graveyard
	if state == "-2":
		return ":cross:"
	elif state == "-1":
		return ":tools:"
	elif state == "0":
		return ":clock1:"
	elif state == "1":
		return ":large_blue_diamond:"
	elif state == "2":
		return ":fire:"
	elif state == "3":
		return ":sweat_drops:"
	elif state == "4":
		return ":heart:"
	else: return ":question:"

async def list_XOR_async(list_1, list_2):
	check_list = list_1 + list_2

	list_1 = [vars(o) for o in list_1]
	list_2 = [vars(o) for o in list_2]

	diffr_list = []

	for obj in check_list:
		if (vars(obj) in list_1 or vars(obj) in list_2) and not (vars(obj) in list_1 and vars(obj) in list_2):
			diffr_list.append(obj)

	return diffr_list

def list_XOR(list_1, list_2):
	list_1 = [hash(o) for o in list_1]
	list_2 = [hash(o) for o in list_2]

	check_list = list_1 + list_2
	diffr_list = []

	for obj in check_list:
		if (hash(obj) in list_1 or hash(obj) in list_2) and not (hash(obj) in list_1 and hash(obj) in list_2):
			diffr_list.append(obj)

	return diffr_list

#OS controll
async def reload_(BASE):
	try:
		BASE.moduls.Console.BLUE("SYSTEM INFO","Reloading Base...")
		BASE.RELOAD = True
		BASE.load_BASE(BASE)
		BASE.moduls.Twitch.alerts(BASE)
		await asyncio.sleep(3)
		setattr(BASE.vars, "app", await BASE.phaaze.application_info() )
		setattr(BASE.vars, "discord_is_NOT_ready", False )
		await asyncio.sleep(5)
		await BASE.phaaze.change_presence(game=discord.Game(type=0, name=BASE.version_nr), status=discord.Status.online)
		BASE.RELOAD = False

	except Exception as e:
		print(str(e.__class__))
		print(str(e))
