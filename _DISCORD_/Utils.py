#BASE.moduls._Discord_.Utils

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

	return c

async def is_Owner(BASE, message):
	v = False
	if message.author == message.server.owner:
		v = True

	return v
#serverfiles
async def get_server_file(BASE, id, prevent_new=False):
	#get
	file = BASE.PhaazeDB.select(of="discord/server_setting", where="data['server_id'] == '{}'".format(id))

	if len(file['data']) == 0:
		#didn't find entry -> make new
		if prevent_new:
			return None
		else:
			return await make_server_file(BASE, id)
	else:
		return file['data'][0]

async def make_server_file(BASE, id):
	insert_ = dict()

	insert_['server_id'] = id,
	insert_['autorole'] = None,

	insert_['welcome_msg'] = None,
	insert_['welcome_msg_priv'] = None,
	insert_['welcome_chan'] = None,

	insert_['leave_msg'] = None,
	insert_['leave_chan'] = None,

	insert_['blacklist'] = [],
	insert_['blacklist_punishment'] = None,

	insert_['ban_links'] = False,
	insert_['ban_links_whitelist'] = [],
	insert_['ban_links_role'] = None,

	insert_['enable_chan_ai'] = [],
	insert_['enable_chan_nsfw'] = [],
	insert_['enable_chan_game'] = [],

	insert_['disable_chan_normal'] = [],
	insert_['disable_chan_mod'] = [],
	insert_['disable_chan_level'] = [],
	insert_['disable_chan_custom'] = [],

	insert_['owner_disable_normal'] = False,
	insert_['owner_disable_mod'] = False,
	insert_['owner_disable_level'] = False,
	insert_['owner_disable_custom'] = False,

	Console.CYAN("INFO", "New serverfile created")

	BASE.PhaazeDB.insert(into="discord/server_setting", content=insert_)

	return insert_

#levelfiles
async def get_server_level_file(BASE, id, prevent_new=False):
	#get
	file = BASE.PhaazeDB.select(of="discord/level/level_"+str(id))

	if file['status'] == "error":
		#didn't find entry -> make new
		if prevent_new:
			return None
		else:
			return await make_server_level_file(BASE, id)
	else:
		return file['data']

async def make_server_level_file(BASE, id):

	BASE.PhaazeDB.create(of="discord/level/level_"+str(id))
	Console.CYAN("INFO", "New serverlevelfile created")

	return []

#customfiles
async def get_server_commands(BASE, id, prevent_new=False):
	#get
	file = BASE.PhaazeDB.select(of="discord/commands/commands_"+str(id))

	if file['status'] == "error":
		#didn't find entry -> make new
		if prevent_new:
			return None
		else:
			return await make_get_server_commands(BASE, id)
	else:
		return file['data']

async def make_get_server_commands(BASE, id):

	BASE.PhaazeDB.create(of="discord/commands/commands_"+str(id))
	Console.CYAN("INFO", "New servercommandsfile created")

	return []

#stuff
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
			["PhaazeWebsite", ":", "Active"],
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
			["Active in:", "{0} Servers".format(str(len(BASE.phaaze.servers)))],
			["Can see:", "{0} unique Members".format(str(await get_unique_members(BASE)))]

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
