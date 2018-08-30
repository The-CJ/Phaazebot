#BASE.modules._Discord_.Utils

import asyncio, Console, discord, tabulate, time

async def return_real_me(BASE, message):
	return discord.utils.get(message.server.members, id=BASE.discord.user.id)

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
async def get_server_setting(BASE, id, prevent_new=False):
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

	insert_['server_id'] = id
	insert_['autorole'] = None

	insert_['welcome_msg'] = None
	insert_['welcome_msg_priv'] = None
	insert_['welcome_chan'] = None

	insert_['leave_msg'] = None
	insert_['leave_chan'] = None

	insert_['blacklist'] = []
	insert_['blacklist_punishment'] = "leave"

	insert_['ban_links'] = False
	insert_['ban_links_whitelist'] = []
	insert_['ban_links_role'] = []

	insert_['enable_chan_ai'] = []
	insert_['enable_chan_nsfw'] = []
	insert_['enable_chan_game'] = []

	insert_['disable_chan_normal'] = []
	insert_['disable_chan_level'] = []
	insert_['disable_chan_custom'] = []
	insert_['disable_chan_quotes'] = []

	insert_['owner_disable_normal'] = False
	insert_['owner_disable_mod'] = False
	insert_['owner_disable_level'] = False
	insert_['owner_disable_custom'] = False

	insert_['track_options'] = []
	insert_['track_channel'] = None

	BASE.modules.Console.INFO("New Discord Server Settings DB entry")

	BASE.PhaazeDB.insert(into="discord/server_setting", content=insert_)

	return insert_

#levelfiles
async def get_server_level(BASE, id, prevent_new=False):
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

	BASE.PhaazeDB.create(name="discord/level/level_"+str(id))
	BASE.modules.Console.INFO("New Discord Server Level DB-Container created")

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

	BASE.PhaazeDB.create(name="discord/commands/commands_"+str(id))
	BASE.modules.Console.INFO("New Discord Server Command DB-Container created")

	return []

#customquotes
async def get_server_quotes(BASE, id, prevent_new=False):
	#get
	file = BASE.PhaazeDB.select(of="discord/quotes/quotes_"+str(id))

	if file['status'] == "error":
		#didn't find entry -> make new
		if prevent_new:
			return None
		else:
			return await make_get_server_quotes(BASE, id)
	else:
		return file['data']

async def make_get_server_quotes(BASE, id):

	BASE.PhaazeDB.create(name="discord/quotes/quotes_"+str(id))
	BASE.modules.Console.INFO("New Discord Server Quote DB-Container created")

	return []

#addrolelist
async def get_server_addrolelist(BASE, id, prevent_new=False):
	#get
	file = BASE.PhaazeDB.select(of="discord/addrole/addrole_"+str(id))

	if file['status'] == "error":
		#didn't find entry -> make new
		if prevent_new:
			return None
		else:
			return await make_server_addrolelist(BASE, id)
	else:
		return file['data']

async def make_server_addrolelist(BASE, id):

	BASE.PhaazeDB.create(name="discord/addrole/addrole_"+str(id))
	BASE.modules.Console.INFO("New Discord Server Quote DB-Container created")

	return []

#stuff
class Phaaze_info(object):
	async def Info(BASE, message, kwargs):
		finish = ""
		finish += f"{BASE.vars.Logo}\n"
		finish += f"{' '*5}{BASE.version}\n"
		finish += f"{' '*5}Uptime: {Phaaze_info.get_uptime(BASE)}\n\n"

		finish += f"Status:\n{Phaaze_info.get_status_tablulate(BASE)}\n\n"

		finish += "-- Stats for Discord --\n\n"

		finish += Phaaze_info.get_discord_infos(BASE)

		finish += f"\n\nContact:\n"
		finish += f"Developer: {str(BASE.vars.app.owner)} | ID: {BASE.vars.app.owner.id}\n"
		finish += f"Mail: admin@phaaze.net\n"
		finish += f"Dev Server: https://discord.gg/ZymrebS | https://discord.me/phaaze\n"

		try:
			await BASE.discord.send_message(message.channel, ":incoming_envelope: -> PM")
			return await BASE.discord.send_message(message.author, f"```{finish}```")

		except:
			pass

	def get_uptime(BASE):
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

	def get_status_tablulate(BASE):
		status = [
			["PhaazeOS", ":", "Active" if BASE.active.main else "Offline"],
			["PhaazeWeb", ":", "Active" if BASE.active.web else "Offline"],
			["PhaazeAPI", ":", "Active" if BASE.active.api else "Offline"],
			["PhaazeDiscord", ":", "Active" if BASE.active.discord else "Offline"],
			["PhaazeTwitchIRC", ":", "Active" if BASE.active.twitch_irc else "Offline"],
			["PhaazeTwitchAlerts", ":", "Active" if BASE.active.twitch_alert else "Offline"],
			["PhaazeAI", ":", "Active" if BASE.active.ai else "Offline"],
			["PhaazeMusic", ":", "Active" if BASE.active.music else "Offline"],
			["PhaazeOsu!Functions", ":", "Active" if BASE.active.osu else "Offline"],
			["PhaazeOsu!IRC", ":", "Active" if BASE.active.osu_irc else "Offline"],
			["PhaazeTwitter", ":", "Active" if BASE.active.twitter else "Offline"],
			["PhaazeYouTube", ":", "Active" if BASE.active.youtube else "Offline"],
		]

		return tabulate.tabulate(status, tablefmt="plain")

	def get_discord_infos(BASE):
		infos = [
			["Libary", "Rapptz/discord.py - " + discord.__version__],
			["ID:", BASE.discord.user.id],
			["Nickname:", BASE.discord.user.name],
			["Discriminator:", f"#{BASE.discord.user.discriminator}"],
			["Active in:", f"{str(len(BASE.discord.servers))} Servers"],
			["Can see:", f"{Phaaze_info.get_unique_members(BASE)} unique Members"]
		]

		return tabulate.tabulate(infos, tablefmt="plain")

	def get_unique_members(BASE):
		a = []

		for server in BASE.discord.servers:
			for member in server.members:
				if member.id not in a: a.append(member.id)

		return len(a)

	async def About(BASE, message, kwargs):
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
		t.set_thumbnail(url=BASE.discord.user.avatar_url)
		t.set_footer(text="Want more infos? Goto https://phaaze.net", icon_url=app.icon_url)
		t.set_author(name="Phaazebot", url="", icon_url=app.icon_url)

		t.add_field(name="Phaaze for Discord", value="Just click this link and select a server:\n"+Admin_invite, inline=False)
		t.add_field(name="Phaaze for Twitch", value="Go to http://www.twitch.tv/phaazebot and type `>join` for adding it to your channel", inline=False)
		t.add_field(name="Support Phaaze", value="Phaaze will always be free, support it to keep it that way:\nhttps://www.patreon.com/the_cj", inline=False)
		t.add_field(name="Phaaze Server", value="https://discord.gg/ZymrebS | https://discord.me/phaaze", inline=False)
		return await BASE.discord.send_message(message.channel, embed=t)
