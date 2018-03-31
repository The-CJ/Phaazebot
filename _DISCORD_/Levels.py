#BASE.moduls.levels

import asyncio, discord, json, math, tabulate, datetime

Medalls = {}

class Discord(object):

	async def get_user(file, member):
		for user in file["members"]:
			if user["id"] == member.id:
				return user

		#user was not found --> make new
		user = {
				"id": member.id,
				"exp": 0,
				"medal_custom": [],
				"medal_normal": []
				}
		file["members"].append(user)
		return user

	async def get_exp(lvl):
		return round( 75 + ((lvl * 75) + (lvl * (lvl*5) * 2)) )

	async def get_lvl(exp):
		lvl = 0
		while await Discord.get_exp(lvl) < exp:
			lvl += 1
		return lvl

			#	else:
			#		level = math.floor(-(1 / 20 * (((-math.sqrt(5)) * math.sqrt((8 * exp) + 525)) + 75)))
			#		return level
		pass

	async def Base(BASE, message):
		#still in cooldown
		if message.author.id in BASE.cooldown.SPECIAL_COOLDOWNS.D_LEVELS: return
		#is a command
		if message.content.startswith(BASE.vars.PT): return
		#add to colldown
		BASE.cooldown.SPECIAL_COOLDOWNS.D_LEVELS.append(message.author.id)

		#load file
		file = await BASE.moduls.Utils.get_server_level_file(BASE, message.server.id)
		if message.channel.id in file["disabled_channels"]: return
		if file["muted"] == 1: return

		#get user
		user = await Discord.get_user(file, message.author)

		user["exp"] += 1

		if user["exp"] >= 1000000: user["exp"] = 1

		#save progress
		with open("LEVELS/DISCORD/{0}.json".format(message.server.id), "w") as save:
			json.dump(file, save)
			setattr(BASE.levelfiles, "level_"+message.server.id, file)

		await Discord.check_level(BASE, message, user)

	async def check_level(BASE, message, user):
			#get level from exp
			current_level = await Discord.get_lvl(user["exp"])
			#needed to next level
			next_lvl_exp = await Discord.get_exp(current_level)

			#on level up
			if next_lvl_exp == user["exp"]:
				try: await BASE.phaaze.send_message(message.channel, message.author.mention + "  is now Level **{0}** :tada:".format(current_level+1))
				except: pass

	async def GetLevelStatus(BASE, message):
		if message.author.bot: return
		m = message.content.split(" ")
		file = await BASE.moduls.Utils.get_server_level_file(BASE, message.server.id)
		if message.channel.id in file["disabled_channels"]: return
		if file["muted"] == 1: return
		disable_l_and_l = file.get("lvl_ask", [])
		if message.channel.id in disable_l_and_l: return

		if message.content.lower().startswith("{0}level calc ".format(BASE.vars.PT)):
			if m[2].isdigit():
				level = int(m[2])-1
				if level != -1:
					xp = await Discord.get_exp(level)
					return await BASE.phaaze.send_message(message.channel, "Level **{0}** = **{1}+** EXP".format(m[2], str(xp)))

		if len(m) == 1:
			user_ = await Discord.get_user(file, message.author)

			current_level = await Discord.get_lvl(user_["exp"])
			next_lvl_exp = await Discord.get_exp(current_level)

			cheated = user_.get("edited", False)

			try:
				user_["medal_custom"] = user_["medal_custom"]
			except:
				user_["medal_custom"] = []

			try:
				user_["medal_normal"] = user_["medal_normal"]
			except:
				user_["medal_normal"] = []

			if len(user_["medal_custom"]) >= 1 or len(user_["medal_normal"]) >= 1: emb = discord.Embed()
			else: emb = None

			if len(user_["medal_normal"]) >= 1: emb.add_field(name="Medals:",value="\n".join("**"+n+"**" for n in user_["medal_normal"]),inline=False)
			if len(user_["medal_custom"]) >= 1:	emb.add_field(name="Custom Medals:",value="\n".join("**"+n+"**" for n in user_["medal_custom"]),inline=False)

			return await BASE.phaaze.send_message(message.channel, embed=emb, content="{0} | Exp: **{1}/{2}** - Level: **{3}**{4}".format(
																					message.author.mention,
																					str(user_["exp"]),
																					str(next_lvl_exp),
																					str(current_level),
																					" [EDITED]" if cheated else "")
																					)

		#by mention
		if len(message.mentions) >= 1:
			if len(message.mentions) > 1:
				return await BASE.phaaze.send_message(message.channel, ":warning: You can not mention multiple members, only 1")
			if not message.mentions[0].id in m[1]:
				return await BASE.phaaze.send_message(message.channel, ":warning: The Member mention must be on first place")
			if message.mentions[0].bot:
				return await BASE.phaaze.send_message(message.channel, ":warning: `{0}` is a Bot, Bots don't have a level".format(message.mentions[0].name))

			user_ = await Discord.get_user(file, message.mentions[0])

			current_level = await Discord.get_lvl(user_["exp"])
			next_lvl_exp = await Discord.get_exp(current_level)

			cheated = user_.get("edited", False)

			try:
				user_["medal_custom"] = user_["medal_custom"]
			except:
				user_["medal_custom"] = []

			try:
				user_["medal_normal"] = user_["medal_normal"]
			except:
				user_["medal_normal"] = []

			if len(user_["medal_custom"]) >= 1 or len(user_["medal_normal"]) >= 1: emb = discord.Embed(title="-")
			else: emb = None

			if len(user_["medal_normal"]) >= 1: emb.add_field(name="Medals:",value="\n".join("**"+n+"**" for n in user_["medal_normal"]),inline=False)
			if len(user_["medal_custom"]) >= 1:	emb.add_field(name="Custom Medals:",value="\n".join("**"+n+"**" for n in user_["medal_custom"]),inline=False)

			return await BASE.phaaze.send_message(message.channel, embed=emb, content="`{0}` | Exp: **{1}/{2}** - Level: **{3}**{4}".format(
																					message.mentions[0].name,
																					str(user_["exp"]),
																					str(next_lvl_exp),
																					str(current_level),
																					" [EDITED]" if cheated else ""
																						)
																					)

		#by id or number
		elif m[1].isdigit() and len(m) == 2:
			member = discord.utils.get(message.server.members, id=m[1])
			if member == None:
				return await BASE.phaaze.send_message(message.channel, ":warning: The ID search didn't find anything.")
			if member.bot:
				return await BASE.phaaze.send_message(message.channel, ":warning: `{0}` is a Bot, Bots don't have a level".format(member.name))

			user_ = await Discord.get_user(file, member)

			current_level = await Discord.get_lvl(user_["exp"])
			next_lvl_exp = await Discord.get_exp(current_level)

			cheated = user_.get("edited", False)

			try:
				user_["medal_custom"] = user_["medal_custom"]
			except:
				user_["medal_custom"] = []

			try:
				user_["medal_normal"] = user_["medal_normal"]
			except:
				user_["medal_normal"] = []

			if len(user_["medal_custom"]) >= 1 or len(user_["medal_normal"]) >= 1: emb = discord.Embed(title="-")
			else: emb = None

			if len(user_["medal_normal"]) >= 1: emb.add_field(name="Medals:",value="\n".join("**"+n+"**" for n in user_["medal_normal"]),inline=False)
			if len(user_["medal_custom"]) >= 1:	emb.add_field(name="Custom Medals:",value="\n".join("**"+n+"**" for n in user_["medal_custom"]),inline=False)

			return await BASE.phaaze.send_message(message.channel, embed=emb, content="`{0}` | Exp: **{1}/{2}** - Level: **{3}**{4}".format(
																					member.name,
																					str(user_["exp"]),
																					str(next_lvl_exp),
																					str(current_level),
																					" [EDITED]" if cheated else ""
																					))

		#by name
		else:
			member = discord.utils.get(message.server.members, name=" ".join(f for f in m[1:]))
			if member == None:
				return await BASE.phaaze.send_message(message.channel, ":warning: The Name search didn't find anything.")
			if member.bot:
				return await BASE.phaaze.send_message(message.channel, ":warning: `{0}` is a Bot, Bots don't have a level".format(member.name))

			user_ = await Discord.get_user(file, member)

			current_level = await Discord.get_lvl(user_["exp"])
			next_lvl_exp = await Discord.get_exp(current_level)

			cheated = user_.get("edited", False)

			try:
				user_["medal_custom"] = user_["medal_custom"]
			except:
				user_["medal_custom"] = []

			try:
				user_["medal_normal"] = user_["medal_normal"]
			except:
				user_["medal_normal"] = []

			if len(user_["medal_custom"]) >= 1 or len(user_["medal_normal"]) >= 1: emb = discord.Embed(title="-")
			else: emb = None

			if len(user_["medal_normal"]) >= 1: emb.add_field(name="Medals:",value="\n".join("**"+n+"**" for n in user_["medal_normal"]),inline=False)
			if len(user_["medal_custom"]) >= 1:	emb.add_field(name="Custom Medals:",value="\n".join("**"+n+"**" for n in user_["medal_custom"]),inline=False)

			return await BASE.phaaze.send_message(message.channel, embed=emb, content="`{0}` | Exp: **{1}/{2}** - Level: **{3}**{4}".format(
																					member.name,
																					str(user_["exp"]),
																					str(next_lvl_exp),
																					str(current_level),
																					" [EDITED]" if cheated else ""
																					))

	async def add_medal(BASE, message, user=None, medal=None, index=None, type="normal"):
		if type == "custom" and index == None and medal != None:
			file = await BASE.moduls.Utils.get_server_level_file(BASE, message.server.id)
			user_ = await Discord.get_user(file, user)
			try:
				user_["medal_custom"] = user_["medal_custom"]
			except:
				user_["medal_custom"] = []

			if medal in user_["medal_custom"]: return await BASE.phaaze.send_message(message.channel, ":warning: The User already has a medal named like this.")
			if len(user_["medal_custom"]) >= 10: return await BASE.phaaze.send_message(message.channel, ":no_entry_sign: Users have a maximum of 10 custom medals.")
			if len(medal) > 75: return await BASE.phaaze.send_message(message.channel, ":no_entry_sign: A custom medal can't be longer than 75 characters.")

			user_["medal_custom"].append(medal)

			with open("LEVELS/DISCORD/{0}.json".format(message.server.id), "w") as save:
				json.dump(file, save)
				setattr(BASE.levelfiles, "level_"+message.server.id, file)

			return await BASE.phaaze.send_message(message.channel, ":white_check_mark: Added **{0}** to `{1}`".format(medal, user.name))

		elif type == "normal" and medal == None and index != None:
			await BASE.phaaze.send_message(message.channel, "Not Jet")

	async def rem_medal(BASE, message, user=None, medal=None, index=None, type="normal"):
		if type == "custom" and index == None and medal != None:
			file = await BASE.moduls.Utils.get_server_level_file(BASE, message.server.id)
			user_ = await Discord.get_user(file, user)
			try:
				user_["medal_custom"] = user_["medal_custom"]
			except:
				user_["medal_custom"] = []

			if medal not in user_["medal_custom"]: return await BASE.phaaze.send_message(message.channel, ":warning: The User doesn't have a custom medal names like this.")

			user_["medal_custom"].remove(medal)

			with open("LEVELS/DISCORD/{0}.json".format(message.server.id), "w") as save:
				json.dump(file, save)
				setattr(BASE.levelfiles, "level_"+message.server.id, file)

			return await BASE.phaaze.send_message(message.channel, ":white_check_mark: Removed **{0}** from `{1}`".format(medal, user.name))

	async def clear_custom(BASE, message, user=None):
		file = await BASE.moduls.Utils.get_server_level_file(BASE, message.server.id)
		user_ = await Discord.get_user(file, user)

		user_["medal_custom"] = []

		with open("LEVELS/DISCORD/{0}.json".format(message.server.id), "w") as save:
			json.dump(file, save)
			setattr(BASE.levelfiles, "level_"+message.server.id, file)

		return await BASE.phaaze.send_message(message.channel, ":white_check_mark: Removed all medals from `{0}`".format(user.name))

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
							str(await Discord.get_lvl(mem["exp"])),
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




