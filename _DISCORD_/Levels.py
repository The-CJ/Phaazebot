#BASE.moduls._Discord_.Levels

import asyncio, discord, json, tabulate, datetime

Medalls = {}

class Calc(object):
	async def get_exp(lvl):
		lvl = int(lvl)
		return round( 75 + ((lvl * 75) + (lvl * (lvl*5) * 2)) )

	async def get_lvl(exp):
		lvl = 0
		while await Calc.get_exp(lvl) < exp:
			lvl += 1
		return lvl

class Utils(object):
	async def get_user(BASE, level_file, server_id, member_id, prevent_new=False):
		for user in level_file:
			if user["member_id"] == member_id:
				return user

		#user was not found --> make new
		user = dict(
				id = member_id,
				exp = 0,
				medal = [],
				edited = False
				)

		if not prevent_new:
			BASE.PhaazeDB.insert(into="discord/level/level_"+server_id, content=user)
			return user
		else:
			return None

	async def check_level(BASE, message, user):
			#get level from exp
			current_level = await Calc.get_lvl(user["exp"])
			#needed to next level
			next_lvl_exp = await Calc.get_exp(current_level)

			#on level up
			if next_lvl_exp == user["exp"]:
				try: return await BASE.phaaze.send_message(message.channel, message.author.mention + "  is now Level **{0}** :tada:".format(current_level+1))
				except: pass

async def Base(BASE, message, server_setting, server_levels):
	#still in cooldown
	if message.author.id in BASE.cooldown.Level_CD: return

	#is a command
	if message.content.startswith(BASE.vars.PT): return

	#are levels disabled?
	if message.channel.id in server_setting.get("disable_chan_level", []): return
	if server_setting.get("owner_disable_level", False): return

	#get user
	user = await Utils.get_user(BASE, server_levels, message.server.id, message.author.id)

	user['exp'] = user.get("exp", 0)
	user["exp"] += 1

	if user["exp"] >= 1000000: user["exp"] = 1

	#save progress
	BASE.PhaazeDB.update(
		of="discord/level/level_"+message.server.id,
		where=f"data['member_id'] == '{user['member_id']}'",
		content=dict(exp=user['exp'])
	)

	#add cooldown
	asyncio.ensure_future(BASE.cooldown.CD_Level(message))

	await Utils.check_level(BASE, message, user)

async def get(BASE, message, kwargs):
	if message.author.bot: return

	if kwargs.get('server_setting', {}).get('owner_disable_level', False): return
	if message.channel.id in kwargs.get('server_setting', {}).get('disable_chan_level', []): return

	m = message.content.split(" ")

	if message.content.lower().startswith(f"{BASE.vars.PT}level calc "):
		if m[2].isdigit():
			level = int(m[2])-1
			if level != -1:
				xp = await Calc.get_exp(level)
				return await BASE.phaaze.send_message(message.channel, f"Level **{m[2]}** = **{str(xp)}+** EXP")

	user = None

	#self
	if len(m) == 1:
		user = message.author

	#mention
	if user == None and message.mentions:
		user = message.mentions[0]

	#id or name
	if user == None and len(m) > 1:
		if m[1].isdigit():
			user = discord.utils.get(message.server.members, id=m[1])

		else:
			user = discord.utils.get(message.server.members, name="".join(s for s in m[1:]))

	if user == None:
		return await BASE.phaaze.send_message(message.channel, f":warning: Could not find a valid user.\n`{BASE.vars.PT} [Option]`\n`[Option]` can be empty, @ mention, ID or the full member name.")


	# # #
	level_user = await Utils.get_user(BASE, kwargs.get('server_levels', []), message.server.id, user.id, prevent_new=True)

	if level_user == None:
		return await BASE.phaaze.send_message(message.channel, f":warning: Seems like there is no level for `{user.name}`\nMaybe the user never typed anything or got deleted.")

	exp_current = level_user.get('exp', 0)
	level_current = await Calc.get_lvl(exp_current)
	exp_next = await Calc.get_exp(level_current)
	edited = " [EDITED]" if level_user.get('edited', False) else ""

	return await BASE.phaaze.send_message(message.channel, f"💠 `{user.name}` **LVL: {str(level_current)}** - EXP: {str(exp_current)} / {str(exp_next)}.{edited}")

async def leaderboards(BASE, message):
	m = message.content.split(" ")
	file = await BASE.moduls.Utils.get_server_level_file(BASE, message.server.id)
	if message.channel.id in file["disabled_channels"]: return
	if file["muted"] == 1: return
	disable_l_and_l = file.get("lvl_ask", [])
	if message.channel.id in disable_l_and_l: return

	many = 5

	if len(m) > 1:
		if m[1].isdigit():
			if 1 <= int(m[1]) <= 15:
				many = int(m[1])
			else:
				return await BASE.phaaze.send_message(message.channel, ":no_entry_sign: The leaderboard's length must be: Min: 1 - Max: 15 or `all`")

		elif m[1].lower() == "all":
			many = int(message.server.member_count)

		else:
			return await BASE.phaaze.send_message(message.channel, ":warning: `{0}` is unsupported, leaderboard's length must be: Min: 1 - Max: 15 or `all`".format(m[1]))

	members_on_server = [mm.id for mm in message.server.members if not mm.bot]
	members_to_list = []

	for user in file["members"]:
		if user["id"] in members_on_server:
			members_to_list.append(user)

	if len(members_to_list) == 0:
		return await BASE.phaaze.send_message(message.channel, ":question: Seems like there are no member with level for a leaderboard :(")

	members_to_list = sorted(members_to_list, key=lambda exp: exp["exp"], reverse=True)

	#check if not to long
	if len(members_to_list) < many:
		many = len(members_to_list)

	finshed_list = members_to_list[:many]

	def get_user_name(_id):
		for n in message.server.members:
			if n.id == _id: return n.name

	l = [["Rank:", "|", "LVL:", "|", "EXP:", "|", "Name:"], ["", "-", "", "-", "", "-", ""]]
	rank = 1
	for mem in finshed_list:
		cheated = mem.get("edited", False)
		x = " [EDITED]" if cheated else ""
		l.append(	[
						"#"+str(rank),
						"|",
						str(await get_lvl(mem["exp"])),
						"|",
						mem["exp"],
						"|",
						get_user_name(mem["id"]) + x
					]
				)
		rank = rank + 1

	return_message = "**Top {0} leaderboard** ```{1}```".format(str(many), tabulate.tabulate(l, tablefmt="plain"))

	if len(return_message) >= 1999:
		now = datetime.datetime.now()
		gist_respone = await BASE.moduls.git_utils.post_gist(
			description="Server level file for Discord Server: {}".format(message.server.name),
			name="level_file_{0}_{1}".format(message.server.id, now.strftime("%Y-%m-%d")),
			content=return_message
			)
		return_message = "Your member leaderboard is way too long, it's been dumped to a GitHub Gist\n\n{}".format(gist_respone)

	return await BASE.phaaze.send_message(message.channel, return_message)




