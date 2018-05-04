#BASE.modules._Discord_.Levels

import asyncio, discord, tabulate

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
			if user.get("member_id", None) == member_id:
				return user

		#user was not found --> make new
		user = dict(
				member_id = member_id,
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
				try: return await BASE.discord.send_message(message.channel, message.author.mention + "  is now Level **{0}** :tada:".format(current_level+1))
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
	if kwargs.get('server_setting', {}).get('owner_disable_level', False) and not await BASE.modules._Discord_.Utils.is_Owner(BASE, message): return
	if message.channel.id in kwargs.get('server_setting', {}).get('disable_chan_level', []) and not await BASE.modules._Discord_.Utils.is_Mod(BASE, message): return

	m = message.content.split(" ")

	if message.content.lower().startswith(f"{BASE.vars.PT}level calc "):
		if m[2].isdigit():
			level = int(m[2])-1
			if level != -1:
				xp = await Calc.get_exp(level)
				return await BASE.discord.send_message(message.channel, f"Level **{m[2]}** = **{str(xp)}+** EXP")

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
		return await BASE.discord.send_message(message.channel, f":warning: Could not find a valid user.Try: `{BASE.vars.PT}level [Option]`\n`[Option]` can be empty, @ mention, ID or the full member name.")

	if user.bot:
		return await BASE.discord.send_message(message.channel, f":no_entry_sign: Bots don't have a level.")

	# # #
	level_user = await Utils.get_user(BASE, kwargs.get('server_levels', []), message.server.id, user.id, prevent_new=True)

	if level_user == None:
		return await BASE.discord.send_message(message.channel, f":warning: Seems like there is no level for `{user.name}`\nMaybe the user never typed anything or got deleted.")

	exp_current = level_user.get('exp', 0)
	level_current = await Calc.get_lvl(exp_current)
	exp_next = await Calc.get_exp(level_current)
	avatar = user.avatar_url if "" != user.avatar_url != None else user.default_avatar_url

	emb = discord.Embed(color=0x00ffdd)
	emb.set_author(name=user.name, icon_url=avatar)

	emb.add_field(name="Level:",value=str(level_current),inline=True)
	emb.add_field(name="Exp:",value=f"{str(exp_current)} / {str(exp_next)}",inline=True)
	if level_user.get('edited', False):
		emb.add_field(name=":warning: EDITED:",value="Exp value got edited.", inline=True)

	if level_user.get('medal', []):
		emb.add_field(name="Medals:",value="\n".join(m for m in level_user.get('medal', [])), inline=False)

	return await BASE.discord.send_message(message.channel, embed=emb)

async def leaderboard(BASE, message, kwargs):
	if kwargs.get('server_setting', {}).get('owner_disable_level', False) and not await BASE.modules._Discord_.Utils.is_Owner(BASE, message): return
	if message.channel.id in kwargs.get('server_setting', {}).get('disable_chan_level', []) and not await BASE.modules._Discord_.Utils.is_Mod(BASE, message): return

	m = message.content.split(" ")
	count = 5

	if len(m) > 1:
		if m[1].isdigit():
			if 1 <= int(m[1]) <= 15:
				count = int(m[1])
			else:
				return await BASE.discord.send_message(message.channel, ":no_entry_sign: The leaderboard's length must be between 1 and 15")

		else:
			return await BASE.discord.send_message(message.channel, f":warning: `{m[1]}` is unsupported, leaderboard's length must be between 1 and 15")

	server_levels = kwargs.get('server_levels', [])
	server_members = [member for member in message.server.members if not member.bot]
	# Be sure saved member is on server
	members_to_list = [member for member in server_levels if member.get('member_id', None) in [s.id for s in server_members] ]

	if len(members_to_list) == 0:
		return await BASE.discord.send_message(message.channel, ":question: Seems like there are no member with level for a leaderboard :(")

	members_to_list = sorted(members_to_list, key=lambda user: user.get("exp", None), reverse=True)

	#check if not to long
	if len(members_to_list) < count:
		count = len(members_to_list)

	finshed_list = members_to_list[:count]

	leaderboard_list = [["Rank:", "|", "LVL:", "|", "EXP:", "|", "Name:"], ["", "-", "", "-", "", "-", ""]]
	rank = 1
	for member in finshed_list:
		edited = member.get("edited", False)
		edited = " [EDITED]" if edited else ""
		user_name = discord.utils.get(message.server.members, id=member.get('member_id', None))
		if user_name == None:
			user_name = "[N/A]"
		else:
			user_name = user_name.name
		leaderboard_list.append( [ "#"+str(rank), "|", str(await Calc.get_lvl(member.get("exp", 0))), "|", str(member.get("exp", 0))+edited, "|", user_name ])
		rank = rank + 1

	table = tabulate.tabulate(leaderboard_list,tablefmt="plain")
	return_message = f"**Top {str(count)} leaderboard** Wanna watch all? :link: https://phaaze.net/discord/level/{message.server.id} ```{table}```"

	return await BASE.discord.send_message(message.channel, return_message)
