##BASE.moduls.Commands
Anti_PM_Spam_Commands = []
import asyncio, json, requests, discord, random, re, datetime
from tabulate import tabulate
import subprocess

async def osu_base(BASE, message):
	m = message.content.lower().split(" ")

	if len(m) == 1:
		return await BASE.phaaze.send_message(message.channel, ":warning: Missing a option!  Usage: `{0}osu [Option]`\n\n Available options: `stats`, `map`, `calc`".format(BASE.vars.PT))

	elif len(m) >= 2:

		if m[1].startswith("stats"):
			if len(m) == 2:
				return await BASE.phaaze.send_message(message.channel, ":warning: Missing User!  Usage: `{0}osu stats(mode) [User - link, name or id]`\n".format(BASE.vars.PT) + '`(mode)` - Can be empty, `/osu`, `/ctb`, `/mania` or `/taiko`')

			else:
				c = m[1].split("/")
				try: mode = c[1]
				except: mode = "osu"

				#set mode
				if mode == "osu": MODE = "0"
				elif mode == "taiko": MODE = "1"
				elif mode == "ctb": MODE = "2"
				elif mode == "mania": MODE = "3"
				elif mode == "": return await BASE.phaaze.send_message(message.channel, ":warning: Option after `stats/` is missing. Available Options are: `osu,ctb,mania,taiko`  Or leave it free an remove the `/`.")
				else: return await BASE.phaaze.send_message(message.channel, ":warning: `{0}` is not a gamemode, Available are: `osu`,`ctb`,`mania`,`taiko`".format(c[1]))

				#get user stuff
				req_user = message.content.split(" ")[2]

				#stuff is a link --> get name/id
				if "osu.ppy.sh/u" in req_user:
					req_user = req_user.split("u/")[1]

				#get_user
				User = await BASE.moduls.osu.get_user(BASE, user=req_user, mode=MODE)
				if User == None: return await BASE.phaaze.send_message(message.channel, ":warning: The given User could not found!")

				stuff = ":globe_with_meridians: #{rank}  -  :flag_{country}: #{country_rank}\n"\
						":part_alternation_mark: {pp} pp\n"\
						":dart: {acc}% Accuracy\n"\
						":military_medal: Level: {level}\n"\
						":timer: Playcount: {playcount}\n"\
						":chart_with_upwards_trend: Ranked Score: {ranked_score}\n"\
						":card_box: Total Score: {total_score}\n"\
						":id: {user_id}".format(
										rank = "{:,}".format(int(User.rank)) if User.rank != None else "N/A",
										country = User.country,
										country_rank = "{:,}".format(int(User.country_rank)) if User.country_rank != None else "N/A",
										pp = "{:,}".format(round(float(User.pp), 2)) if User.pp != None and User.pp != "0" else "N/A",
										acc = str(round(float(User.acc), 2)) if User.acc != None else "N/A",
										level = str(round(float(User.level), 1)) if User.level != None else "N/A",
										playcount = "{:,}".format(int(User.playcount)) if User.playcount != None else "N/A",
										ranked_score = "{:,}".format(int(User.ranked_score)) if User.ranked_score != None else "N/A",
										total_score = "{:,}".format(int(User.total_score)) if User.total_score != None else "N/A",
										user_id = User.user_id
										)

				EMB = discord.Embed(
					title=User.name,
					url="https://osu.ppy.sh/u/"+User.user_id,
					color=int(0xFF69B4),
					description=stuff
					)

				if User.count_A != User.count_S != User.count_SS != None != User.count_50 != User.count_100 != User.count_300:
					table_R = 	[
									["A:", "{:,}".format(int(User.count_A))],
									["S:", "{:,}".format(int(User.count_S))],
									["SS:", "{:,}".format(int(User.count_SS))]
								]

					EMB.add_field(name="Ranks:",value="```{}```".format(tabulate(table_R, tablefmt="plain")), inline=True)

				EMB.set_thumbnail(url="https://a.ppy.sh/{0}".format(User.user_id))
				EMB.set_footer(text="Provided by osu!", icon_url="http://w.ppy.sh/c/c9/Logo.png")
				EMB.set_author(name="Stats for: {0}".format(User.mode_name))

				return await BASE.phaaze.send_message(message.channel, content=message.author.mention, embed=EMB)

		elif m[1].startswith("map"):
			if len(m) == 2:
				return await BASE.phaaze.send_message(message.channel, ":warning: Missing Map Link!  Usage: `{0}osu map [map/mapset/mapcreator - LINK]`".format(BASE.vars.PT))

			#find mode and id
			try:
				if "osu.ppy.sh/s/" in m[2]:
					search_id = m[2].split("/s/")[1]
					mode = "s"

				elif "osu.ppy.sh/b/" in m[2]:
					search_id = m[2].split("/b/")[1]
					mode = "b"

				elif "osu.ppy.sh/u/" in m[2]:
					search_id = m[2].split("/u/")[1]
					mode = "u"

				else: 0/0
			except:
				return await BASE.phaaze.send_message(message.channel, ":warning: Invalid or missing Link!  Usage: `{0}osu map [map/mapset/mapcreator - LINK]`".format(BASE.vars.PT))

			#get set/map/creator
			stuff = await BASE.moduls.osu.get_all_maps(BASE, ID=search_id, mode=mode)
			if stuff == None and mode == "u": return await BASE.phaaze.send_message(message.channel, ":warning: The user does not exist or dosn't created any beatmaps".format(BASE.vars.PT))
			if stuff == None: return await BASE.phaaze.send_message(message.channel, ":warning: Invalid or missing Link!  Usage: `{0}osu map [map/mapset/mapcreator - LINK]`".format(BASE.vars.PT))

			#one
			if mode == "b" or mode == "s" and len(stuff.all_maps) == 1: #one map
				beatmap = stuff.all_maps[0]
				meep = 	"mapped by {creator}\n\n"\
						"{symbol} **{approved_name}** | :green_heart: Favourite: **{favo}** {source}\n"\
						":star:: **{diff}** | :notes: BPM: **{bpm}** | :stopwatch: Lenght: **{full}** *(Drain: {drain})*\n"\
						":small_red_triangle:CS: {cs} | :small_red_triangle:AR: {ar} | :small_red_triangle:OD: {od} | :small_red_triangle:HP: {hp}\n"\
						"*MapID: {mID} | SetID: {sID}*".format	(
									symbol = await BASE.moduls.Utils.get_osu_status_symbol(beatmap.approved),
									approved_name = beatmap.approved_name,
									creator = beatmap.creator,
									diff = str(round(beatmap.diff, 2)),
									bpm = str(round(beatmap.bpm)),
									cs = str(beatmap.cs),
									ar = str(beatmap.ar),
									od = str(beatmap.od),
									hp = str(beatmap.hp),
									full = str(beatmap.lenght),
									drain = str(beatmap.drain),
									source = "| :triangular_flag_on_post: Source: **" + beatmap.source + "**" if beatmap.source != "" else "",
									favo = beatmap.favos,
									mID = beatmap.Map_ID,
									sID = beatmap.Set_ID
										)

				osu_aw = discord.Embed	(
								color=int(0xFF69B4),
								title=beatmap.version,
								url="https://osu.ppy.sh/b/{0}".format(beatmap.Map_ID),
								description=meep
										)

				osu_aw.set_author(url="https://osu.ppy.sh/b/{0}".format(beatmap.Map_ID) ,name="{0} - {1}".format(beatmap.artist, beatmap.title))
				osu_aw.set_footer(text="Provided by osu!", icon_url="http://w.ppy.sh/c/c9/Logo.png")
				osu_aw.set_thumbnail(url="https://b.ppy.sh/thumb/{0}l.jpg".format(beatmap.Set_ID))

				pp_100 = await BASE.moduls.osu_utils.get_pp(beatmap.Map_ID, acc=100.0)
				pp_99 = await BASE.moduls.osu_utils.get_pp(beatmap.Map_ID, acc=99.0)
				pp_98 = await BASE.moduls.osu_utils.get_pp(beatmap.Map_ID, acc=98.0)

				osu_aw.add_field(name="PPcalc:",value="{pp_100}pp for 100% | {pp_99}pp for 99% | {pp_98}pp for 98%...\n`{PT}osu calc [maplink] (options)`".format	(
																																									PT = BASE.vars.PT,
																																									pp_100 = str(round(float(pp_100.pp), 2)),
																																									pp_99 = str(round(float(pp_99.pp), 2)),
																																									pp_98 = str(round(float(pp_98.pp), 2))

																																										), inline=True)

				if not beatmap.tags == []:
					osu_aw.add_field(name="Tags:",value=", ".join(tag for tag in beatmap.tags), inline=True)

				return await BASE.phaaze.send_message(message.channel, embed=osu_aw)


			#set
			elif mode == "s":
				base_infos = stuff.map_sets[0][0]

				listi = []
				for map_ in sorted(stuff.map_sets[0], key=lambda map__: map__.diff):
					diff = "★ " + str(round(map_.diff, 2))
					cs = "CS: " + str(round(map_.cs, 2))
					ar = "AR: " + str(round(map_.ar, 2))
					hp = "HP: " + str(round(map_.hp, 2))
					od = "OD: " + str(round(map_.od, 2))
					_id = "ID: " + str(map_.Map_ID)
					listi.append([map_.version, "|", cs, "|", ar, "|", hp, "|", od, "|", diff, "|", _id])

				fff = 	"**{artist} - {title}**\n"\
						"Mapset by: **{creator}** | {symbol} **{approved_name}** - BPM: **{bpm}**\n"\
						"```{diff_list}```".format	(
											creator = base_infos.creator,
											symbol = await BASE.moduls.Utils.get_osu_status_symbol(base_infos.approved),
											approved_name = base_infos.approved_name,
											artist = base_infos.artist,
											title = base_infos.title,
											diff_list = tabulate(listi, tablefmt="plain"),
											bpm = str(round(base_infos.bpm)))

				ggt = discord.Embed(title="Check it out", url="https://osu.ppy.sh/s/{0}".format(base_infos.Set_ID), color=int(0xFF69B4))

				if len(fff) > 1997: fff = ":no_entry_sign: Seems like this Mapset has to many diffs, its to much for the Discord message limit, sorry."

				return await BASE.phaaze.send_message(message.channel, content=fff, embed=ggt)


			#creator
			elif mode == "u":
				base_infos = stuff.map_sets[0][0]
				base_res = "All Maps by **{0}**\n\n".format(base_infos.creator)

				for _set in stuff.map_sets:

					listi = []

					for map_ in sorted(_set, key=lambda map__: map__.diff):
						diff = "★ " + str(round(map_.diff, 2))
						cs = "CS: " + str(round(map_.cs, 2))
						ar = "AR: " + str(round(map_.ar, 2))
						hp = "HP: " + str(round(map_.hp, 2))
						od = "OD: " + str(round(map_.od, 2))
						_id = "ID: " + str(map_.Map_ID)
						listi.append([map_.version, "|", diff])

					base_res  = base_res + "**{artist} - {title}** | https://osu.ppy.sh/s/{IDD}\n{symbol} **{approved_name}** - BPM: **{bpm}**\n```{diff_list}```\n".format	(
																													artist = _set[0].artist,
																													title = _set[0].title,
																													symbol = await BASE.moduls.Utils.get_osu_status_symbol(_set[0].approved),
																													approved_name = _set[0].approved_name,
																													bpm = str(round(_set[0].bpm)),
																													diff_list = tabulate(listi, tablefmt="plain"),
																													IDD = _set[0].Set_ID
																															)
				ebb = discord.Embed(
						color=int(0xFF69B4),
						title="See them all",
						url="https://osu.ppy.sh/u/{0}".format(base_infos.creator))

				if len(base_res) > 1997: base_res = ":no_entry_sign: Seems like **{0}** made to many Maps, its to much for the Discord message limit, sorry.".format(base_infos.creator)

				await BASE.phaaze.send_message(message.channel, content=base_res, embed=ebb)
				try: await BASE.phaaze.delete_message(message)
				except: pass
				return

		elif m[1].startswith("track"):
			return await BASE.phaaze.send_message(message.channel, ':cold_sweat: Sorry but the "track" modul is under construction! SOON:tm:')

		elif m[1].startswith("calc"):
			await BASE.moduls.osu.pp_calc_for_maps(BASE, message)

		else:
			return await BASE.phaaze.send_message(message.channel, ":warning: `{0}` is not a option!  Available options: `stats`,`map` and `track`".format(m[1]))

async def define(BASE, message):
	LINK = "https://mashape-community-urban-dictionary.p.mashape.com/define"
	TERM = "?term="
	Header = {'X-Mashape-Key': 'QJTGDG2sq1mshRboJDmAcVsa6GEKp1ccIyNjsnhK1IDnMq1KMR'}

	m = message.content.split(" ")
	mm = message.content.lower().split(" ")

	if len(m) == 1:
		return await BASE.phaaze.send_message(message.channel, ':warning: You need to define a word. `{0}define [thing]`'.format(BASE.vars.PT))

	else:
		thing = " ".join(g for g in m[1:])

		if "phaaze" in mm or "phaazebot" in mm:
			return await BASE.phaaze.send_message(message.channel, "Thats me :D")


		res = requests.get(LINK+TERM+thing, headers= Header).json()
	#0 result
		if len(res["list"]) == 0:
			return await BASE.phaaze.send_message(message.channel, ":x: Sorry, but Urban dictionary don't know what: `{0}` is".format(thing))

		else:
			Result = ":notebook_with_decorative_cover:   **{0}**:\n\n"

			top = res["list"][0]["definition"]
			example = res["list"][0]["example"]

			rest_list = res["list"][1:]

			if len(rest_list) == 0:
				return await BASE.phaaze.send_message(message.channel, Result.format(thing) + ":book:: {0}\n\ne.g.: *{1}*".format(top, example))
			else:
				if len(res["list"]) > 1: More = discord.Embed(title="and {0} other definitions".format(str(len(rest_list))), url="http://www.urbandictionary.com/define.php?term="+thing.replace(" ", "+"))
				else: More = None

				return await BASE.phaaze.send_message(message.channel, embed=More, content=Result.format(thing) + ":book:: {0}\n\ne.g.: *{1}*".format(top, example))

async def commands_base(BASE, message):
	if message.author.id in Anti_PM_Spam_Commands:
		return

	Anti_PM_Spam_Commands.append(message.author.id)

	try: await BASE.phaaze.send_message(message.channel, ":incoming_envelope: --> PM")
	except: pass

	level = 1
	if await BASE.moduls.Utils.is_Mod(BASE, message):level = 2
	if await BASE.moduls.Utils.is_Owner(BASE, message): level = 3

	if level == 1:
		norm = await BASE.moduls.Utils.get_Normal_Commands(BASE, message)
		head = "Accessible Commands for you on: `{0}`".format(message.server.name)

		norm.set_author(name="Commands", icon_url=BASE.vars.app.icon_url)
		norm.set_footer(text="▶ Only returned Normal commands, you don't have access to high commands".format(BASE.vars.PT))
		#
		try: await BASE.phaaze.send_message(message.author, content=head, embed=norm)
		except: pass
		##
		await asyncio.sleep(10)
		Anti_PM_Spam_Commands.remove(message.author.id)

	if level == 2:
		norm = await BASE.moduls.Utils.get_Normal_Commands(BASE, message)
		mod = await BASE.moduls.Utils.get_Mods_Commands(BASE, message)
		head = "Accessible Commands for you on: `{0}`".format(message.server.name)

		norm.set_author(name="Commands", icon_url=BASE.vars.app.icon_url)
		mod.set_footer(text="▶ Returned Normal and Mod commands, because you don't have access to owner commands".format(BASE.vars.PT))
		#
		try: await BASE.phaaze.send_message(message.author, content=head, embed=norm)
		except: pass
		##
		await asyncio.sleep(2)
		#
		try: await BASE.phaaze.send_message(message.author, embed=mod)
		except: pass
		##
		await asyncio.sleep(20)
		Anti_PM_Spam_Commands.remove(message.author.id)

	if level == 3:
		norm = await BASE.moduls.Utils.get_Normal_Commands(BASE, message)
		mod = await BASE.moduls.Utils.get_Mods_Commands(BASE, message)
		owner = await BASE.moduls.Utils.get_Owner_Commands(BASE, message)
		head = "Accessible Commands for you on: `{0}`".format(message.server.name)

		norm.set_author(name="Commands", icon_url=BASE.vars.app.icon_url)
		owner.set_footer(text="▶ Returned all available commands".format(BASE.vars.PT))
		#
		try: await BASE.phaaze.send_message(message.author, content=head, embed=norm)
		except: pass
		##
		await asyncio.sleep(2)
		#
		try: await BASE.phaaze.send_message(message.author, embed=mod)
		except: pass
		##
		await asyncio.sleep(2)
		#
		try: await BASE.phaaze.send_message(message.author, embed=owner)
		except: pass
		##
		await asyncio.sleep(30)
		Anti_PM_Spam_Commands.remove(message.author.id)

async def quotes(BASE, message):
	m = message.content.split(" ")

	file = await BASE.moduls.Utils.get_server_file(BASE, message.server.id)

	try:
		file["quotes"] = file["quotes"]
	except:
		file["quotes"] = []

	if len(file["quotes"]) == 0:
		i = await BASE.phaaze.send_message(message.channel, ":grey_exclamation: This server don't have any quotes.")
		await asyncio.sleep(5)
		return await BASE.phaaze.delete_message(i)

	if len(m) == 1:
		qoute = random.choice( file["quotes"] )
		o = [i for i,x in enumerate(file["quotes"]) if x == qoute]
		emb = discord.Embed(description=qoute["content"], colour = int(0xCECEF6))
		emb.set_footer(text="Quote #" + "".join(str(i+1) for i in o))
		return await BASE.phaaze.send_message(message.channel, embed=emb)

	if len(m) >= 2:
		ll = len(file["quotes"])

		if m[1].isdigit():
			nr = int(m[1])
			if nr > ll:
				nr = random.choice(range(1, ll))
		else:
			nr = random.choice(range(1, ll))

		qoute = file["quotes"][nr-1]
		o = [i for i,x in enumerate(file["quotes"]) if x == qoute]
		emb = discord.Embed(description=qoute["content"], colour = int(0xCECEF6))
		emb.set_footer(text="Quote #" + "".join(str(i+1) for i in o))
		return await BASE.phaaze.send_message(message.channel, embed=emb)

async def emotes(BASE, message):
	server_emotes = [e for e in message.server.emojis if not e.managed]
	server_emotes_L = len(server_emotes)
	by_twitch = [e for e in message.server.emojis if e.managed]
	by_twitch_L = len(by_twitch)

	if by_twitch_L == 0 == server_emotes_L:
		return await BASE.phaaze.send_message(message.channel, ":x: This Server has no Custom Emotes")

	if server_emotes_L > 0:
		server_e = "Server Custom Emotes: **{0}**\n\n{1}".format(
									str(server_emotes_L),
									"  |  ".join(str(e) + " - `" + e.name + "`" for e in sorted(server_emotes, key=lambda e: e.name)))
	else: server_e = ""

	if by_twitch_L > 0:
		twitch_e = "\nTwitch Integration Emotes: **{0}**\n\n{1}".format(
									str(by_twitch_L),
									"  |  ".join(str(e) + " - `" + e.name + "`" for e in sorted(by_twitch, key=lambda e: e.name)))
	else: twitch_e = ""

	w = server_e + twitch_e

	return await BASE.phaaze.send_message(message.channel, w[:1999])

async def choice(BASE, message):
	m = message.content.split(" ")
	if len(m) == 1:
		return await BASE.phaaze.send_message(message.channel, ":warning: Missing arguments, at least 2 options separated by \";\" are needed")

	M = message.content.split(" ", 1)[1].split(";")

	for item in M:
		item.replace(" ","")
		item.replace("	","")

	try:
		M.remove("")
	except:
		pass

	if len(M) == 1:
		return await BASE.phaaze.send_message(message.channel, ":warning: Missing arguments, at least 2 options separated by \";\" are needed")

	winner = random.choice(M)
	winner = winner.replace("`", "")
	winner = winner.replace("@everyone", "")
	winner = winner.replace("**", "")

	resp = "And the winner is...\n\n:game_die:- **{}** -:8ball:".format(winner)

	return await BASE.phaaze.send_message(message.channel, resp)

class doujin(object):

	async def request(BASE, message):
		m = message.content.lower()
		m = m.replace("\n", " ")

		if 	m == "{0}doujin".format(BASE.vars.PT) or m == "{0}doujin <".format(BASE.vars.PT):
			return await doujin.errors.no_define(BASE,message)

		if 	m == "{0}doujin help".format(BASE.vars.PT) or\
			m == "{0}doujin <help".format(BASE.vars.PT):
			return await doujin.help(BASE,message)

		if 	m == "{0}doujin <r".format(BASE.vars.PT) or\
			m == "{0}doujin <random".format(BASE.vars.PT) or\
			m == "{0}doujin r".format(BASE.vars.PT) or\
			m == "{0}doujin random".format(BASE.vars.PT):
			return await doujin.random(BASE,message)

		#parse all
		parameter = await doujin.parse(BASE,message)

		#if errors
		if parameter.error == "no_options":
			return await doujin.errors.no_options(BASE,message)

		if parameter.error == "unkown_option":
			return await doujin.errors.unkown_option(BASE, message, parameter.error_text)

		if parameter.error == "missing_value":
			return await doujin.errors.missing_value(BASE, message, parameter.error_text)

		if parameter.error == "page_error_to_much":
			return await doujin.errors.page_error_to_much(BASE, message, parameter.error_text)

		if parameter.error == "page_error_no_digit":
			return await doujin.errors.page_error_no_digit(BASE, message, parameter.error_text)

		if parameter.error == "star_error_to_much":
			return await doujin.errors.star_error_to_much(BASE, message, parameter.error_text)

		if parameter.error == "star_error_no_digit":
			return await doujin.errors.star_error_no_digit(BASE, message, parameter.error_text)

		if parameter.error == "no_anime_found":
			return await doujin.errors.no_anime_found(BASE, message, parameter.error_text)

		if parameter.error == "no_char_found":
			return await doujin.errors.no_char_found(BASE, message, parameter.error_text)

		#make API call
		result = await doujin.Tsumino_call(BASE, message, parameter)

		if result["Data"] == []:
			I =  await BASE.phaaze.send_message(message.channel, ":x: No Books found")
			await asyncio.sleep(15)
			await BASE.phaaze.delete_message(I)

		else:
			await doujin.format_and_send_message(BASE, message, result)

	async def parse(BASE,message):
		class perms:
			error = False
			error_text = None

		m = message.content.lower().split("<")
		m.remove(m[0])

		if len(m) == 0:
			setattr(perms, "error", "no_options")
			return perms

		for term in m:
			term = term.split(" ")
			try:
				term.remove("")
			except:
				pass

		#tag add
			if term[0] == "i" or term[0] == "it" or term[0] == "itag" or\
				term[0] == "itags" or term[0] == "i_t" or\
				term[0] == "i_tag" or term[0] == "i_tags":

				option = term[0]
				term.remove(term[0])

				if len(term) == 0:
					setattr(perms, "error", "missing_value")
					setattr(perms, "error_text", option)
					return perms
				else:
					setattr(perms, "i_tags", term)
		#tag ex
			elif term[0] == "e" or term[0] == "et" or term[0] == "etag" or\
				term[0] == "etags" or term[0] == "e_t" or\
				term[0] == "e_tag" or term[0] == "e_tags":

				option = term[0]
				term.remove(term[0])

				if len(term) == 0:
					setattr(perms, "error", "missing_value")
					setattr(perms, "error_text", option)
					return perms
				else:
					setattr(perms, "e_tags", term)
		#page min
			elif term[0] == "pmin" or term[0] == "p_min" or\
				term[0] == "page_minimum" or term[0] == "page_min":

				option = term[0]
				term.remove(term[0])

				if len(term) == 0:
					setattr(perms, "error", "missing_value")
					setattr(perms, "error_text", option)
					return perms

				if len(term) > 1:
					setattr(perms, "error", "page_error_to_much")
					setattr(perms, "error_text", option)
					return perms

				if not term[0].isdigit():
					setattr(perms, "error", "page_error_no_digit")
					setattr(perms, "error_text", option)
					return perms
				else:
					setattr(perms, "pmin", term[0])
		#page max
			elif term[0] == "pmax" or term[0] == "p_max" or\
				term[0] == "page_maximum" or term[0] == "page_max":

				option = term[0]
				term.remove(term[0])

				if len(term) == 0:
					setattr(perms, "error", "missing_value")
					setattr(perms, "error_text", option)
					return perms

				if len(term) > 1:
					setattr(perms, "error", "page_error_to_much")
					setattr(perms, "error_text", option)
					return perms

				if not term[0].isdigit():
					setattr(perms, "error", "page_error_no_digit")
					setattr(perms, "error_text", option)
					return perms

				else:
					setattr(perms, "pmax", term[0])
		#stars
			elif term[0] == "star" or term[0] == "s" or term[0] == "stars":

				option = term[0]
				term.remove(term[0])

				if len(term) == 0:
					setattr(perms, "error", "missing_value")
					setattr(perms, "error_text", option)
					return perms

				if len(term) > 1:
					setattr(perms, "error", "star_error_to_much")
					setattr(perms, "error_text", option)
					return perms

				if not term[0].isdigit():
					setattr(perms, "error", "star_error_no_digit")
					setattr(perms, "error_text", option)
					return perms

				else:
					if int(term[0]) > 5 or int(term[0]) < 0:
						setattr(perms, "error", "star_error_no_digit")
						setattr(perms, "error_text", option)
						return perms

					setattr(perms, "stars", term[0])
		#anime
			elif term[0] == "a" or term[0] == "anime" or term[0] == "animes":

				option = term[0]
				term.remove(term[0])

				if len(term) == 0:
					setattr(perms, "error", "missing_value")
					setattr(perms, "error_text", option)
					return perms

				animes = []

				for search in term:
					option = search
					anime = requests.get("http://tsumino.com/api/tag?term={0}".format(search.replace("_", "+")))
					anime = anime.json()

					hits = 0
					for res in anime["Data"]:
						if res["Type"] == 6:
							hits = hits + 1
							animes.append(res["Name"])
							break

					if hits == 0:
						setattr(perms, "error", "no_anime_found")
						setattr(perms, "error_text", option)
						return perms

				setattr(perms, "animes", animes)
		#chars
			elif term[0] == "c" or term[0] == "char" or term[0] == "chars" or\
				term[0] == "characters" or term[0] == "character":

				option = term[0]
				term.remove(term[0])

				if len(term) == 0:
					setattr(perms, "error", "missing_value")
					setattr(perms, "error_text", option)

				chars = []

				for search in term:
					option = search
					chars__ = requests.get("http://tsumino.com/api/tag?term={0}".format(search.replace("_", "+")))
					chars__ = chars__.json()

					hits = 0
					for res in chars__["Data"]:
						if res["Type"] == 7:
							hits = hits + 1
							chars.append(res["Name"])
							break

					if hits == 0:
						setattr(perms, "error", "no_char_found")
						setattr(perms, "error_text", option)
						return perms

				setattr(perms, "chars", chars)
		#=
			elif term[0] == "=":

				option = term[0]
				term.remove(term[0])

				if len(term) == 0:
					setattr(perms, "error", "missing_value")
					setattr(perms, "error_text", option)
					return perms

				setattr(perms, "raw", " ".join(f for f in term))
		#nothing
			else:
				setattr(perms, "error", "unkown_option")
				setattr(perms, "error_text", term[0])
				return perms

		##nextup
		return perms

	async def Tsumino_call(BASE, message, parameter):
		MAIN = "https://www.tsumino.com/api/book?SortOptions=Random"
		SEARCH = ""

		if hasattr(parameter, "i_tags"):
			SEARCH = SEARCH + "".join("&TagInclude=" +f	for f in parameter.i_tags)

		if hasattr(parameter, "e_tags"):
			SEARCH = SEARCH + "".join("&TagExclude=" +f	for f in parameter.e_tags)

		if hasattr(parameter, "pmin"):
			SEARCH = SEARCH + "&PageMinimum="+parameter.pmin

		if hasattr(parameter, "pmax"):
			SEARCH = SEARCH + "&PageMaximum="+parameter.pmax

		if hasattr(parameter, "stars"):
			SEARCH = SEARCH + "&RateMinimum=" + parameter.stars

		if hasattr(parameter, "animes"):
			SEARCH = SEARCH + "".join("&Parodies=" + f for f in parameter.animes)

		if hasattr(parameter, "chars"):
			SEARCH = SEARCH + "".join("&Characters=" + f for f in parameter.chars)

		if hasattr(parameter, "raw"):
			SEARCH = SEARCH + "&Search=" + parameter.raw

		site = requests.get(MAIN+SEARCH)
		return site.json()

	async def format_and_send_message(BASE, message, result):
		Book = result["Data"][0]

		pages = Book["Object"]["Pages"]
		tags = " | ".join("`"+f+"`" for f in Book["Object"]["Tags"])
		artist = " | ".join("`"+f+"`" for f in Book["Object"]["Artists"])

		if not Book["Object"]["Characters"] == []:
			chars = "\n:restroom: : "+" | ".join("`"+h+"`" for h in Book["Object"]["Characters"])
		else:
			chars = ""
		if not Book["Object"]["Parodies"] == []:
			animes = "\n:book: : "+" | ".join("`"+h+"`" for h in Book["Object"]["Parodies"])
		else:
			animes = ""
		stars = str(round(Book["Object"]["Rating"], 1))
		if stars == "0.0":
			stars = "N/A"


		dece = 	":page_facing_up: : {1}     :star: : {0}    :paintbrush: : {5}"\
				"{3}{2}"\
				"\n:label: : {4}".format(stars, pages, chars, animes, tags, artist)


		emb = discord.Embed(
						title=":diamond_shape_with_a_dot_inside:" +Book["Object"]["Title"],
						url=Book["Meta"]["Info"],
						colour=int(0x22a7f0),
						description=dece
						)
		emb.set_image(url=Book["Meta"]["Thumb"])
		emb.set_footer(text="Provided by Tsumino", icon_url="http://www.tsumino.com/content/res/logo.png")

		return await BASE.phaaze.send_message(message.channel, embed=emb)

	async def random(BASE,message):
		MAIN = "https://www.tsumino.com/api/book?SortOptions=Random"
		site = requests.get(MAIN)
		return await doujin.format_and_send_message(BASE, message, site.json())

	async def help(BASE,message):
		try: await BASE.phaaze.send_message(message.channel, ":incoming_envelope: --> PM")
		except: pass
		return await BASE.phaaze.send_message(message.author, BASE.vars.doujin_help)

	class errors:
		async def no_options(BASE,message):
			I = await BASE.phaaze.send_message(message.channel, ":warning: You need to define at least one option!\nUse `{0}doujin help` for a list of all options.".format(BASE.vars.PT))
			await asyncio.sleep(15)
			await BASE.phaaze.delete_message(I)

		async def unkown_option(BASE, message, var):
			I = await BASE.phaaze.send_message(message.channel, ":warning: `<{1}` is not a option!\nUse `{0}doujin help` for a list of all options.".format(BASE.vars.PT, var))
			await asyncio.sleep(15)
			await BASE.phaaze.delete_message(I)

		async def missing_value(BASE, message, var):
			I = await BASE.phaaze.send_message(message.channel, ":warning: The option: `<{1}` needs at least one value".format(BASE.vars.PT,var))
			await asyncio.sleep(15)
			await BASE.phaaze.delete_message(I)

		async def page_error_to_much(BASE, message, var):
			I = await BASE.phaaze.send_message(message.channel, ":warning: `<{1}` only takes one number e.g.: 420".format(BASE.vars.PT,var))
			await asyncio.sleep(15)
			await BASE.phaaze.delete_message(I)

		async def page_error_no_digit(BASE, message, var):
			I = await BASE.phaaze.send_message(message.channel, ":warning: `<{1}` can only be a digital number e.g.: 60".format(BASE.vars.PT,var))
			await asyncio.sleep(15)
			await BASE.phaaze.delete_message(I)

		async def star_error_to_much(BASE, message, var):
			I = await BASE.phaaze.send_message(message.channel, ":warning: `<{1}` only takes one number between 1 and 5".format(BASE.vars.PT,var))
			await asyncio.sleep(15)
			await BASE.phaaze.delete_message(I)

		async def star_error_no_digit(BASE, message, var):
			I = await BASE.phaaze.send_message(message.channel, ":warning: `<{1}` can only be a digital number between 1 and 5".format(BASE.vars.PT,var))
			await asyncio.sleep(15)
			await BASE.phaaze.delete_message(I)

		async def no_anime_found(BASE, message, var):
			I = await BASE.phaaze.send_message(message.channel, ":warning: The Anime search: `{0}`, could not be autocomplete. Please be more precise".format(var))
			await asyncio.sleep(15)
			await BASE.phaaze.delete_message(I)

		async def no_char_found(BASE, message, var):
			I = await BASE.phaaze.send_message(message.channel, ":warning: The Character search: `{0}`, could not be autocomplete. Please be more precise".format(var))
			await asyncio.sleep(15)
			await BASE.phaaze.delete_message(I)

		async def no_define(BASE,message):
			I = await BASE.phaaze.send_message(message.channel, ":warning: You need to define at least one option!\nUse `{0}doujin help` for a list of all options.".format(BASE.vars.PT))
			await asyncio.sleep(15)
			await BASE.phaaze.delete_message(I)

class wiki(object):
	async def wiki(BASE, message):
		wikipedia = BASE.moduls.wikipedia

		m = message.content.split(" ")

		#no term
		if len(m) == 1:
			return await BASE.phaaze.send_message(message.channel, ':warning: You need to define a thing you wanna ask. `{0}wikipedia[lang] [thing]`\n`[lang]` - Can be empty or used with a "/" to change the return language e.g.: `{0}wikipedia/de Apfelbaum`, Default is "en"\n`[thing]` - Whatever you wanna search'.format(BASE.vars.PT))

		#set things
		thing = " ".join(g for g in m[1:])
		lang = m[0].split("/")

		#change lang?
		if len(lang) > 1:
			wikipedia.set_lang(lang[1])
			LINK = 'https://' + lang[1].lower() + '.wikipedia.org/wiki/'
		else:
			wikipedia.set_lang("en")
			LINK = 'https://en.wikipedia.org/wiki/'

		#exactly
		try:
			page = wikipedia.page(thing,auto_suggest=False)

			#short it
			text = page.summary[:1900]
			if len(page.summary) > 1900: text = text + ". . . . . :bookmark_tabs: And more."

			#aaaand finished
			send = ":books: **{0}**\n\n{1}".format(page.title,text)
			return await BASE.phaaze.send_message(message.channel, send, embed=discord.Embed(title="Go to the full page.", url=LINK+page.title))

		#recommendations
		except:
			#get hits and recommendations
			list, or_that = wikipedia.search(thing, suggestion=True)

			#0 liste, 0 vorschläge
			if len(list) == 0 and or_that == None:
				return await BASE.phaaze.send_message(message.channel, ":warning: Seems like Wikipedia don't know what: `{}`, is.".format(thing))

			#0 hits, aber autokorrektur
			elif len(list) == 0:
				t =  await BASE.phaaze.send_message(message.channel, ":scroll: Do You mean: `{}`?\n\n:regional_indicator_y: / :regional_indicator_n:".format(or_that))
				choose = await BASE.phaaze.wait_for_message(timeout=30, author=message.author, channel=message.channel)
				if choose != None:
					if choose.content.lower() == "y":
						try:
							page = wikipedia.page(or_that)
						except:
							return await BASE.phaaze.send_message(message.channel, ":warning: Sorry, but an unknown Error just broke the internet, try something else.")

						#short it
						text = page.summary[:1900]
						if len(page.summary) > 1900: text = text + ". . . . . :bookmark_tabs: And more."

						#aaaand finished
						send = ":books: **{0}**\n\n{1}".format(page.title,text)
						return await BASE.phaaze.edit_message(t, new_content=send, embed=None)

			#found one. or two, or 3 or...
			if len(list) > 0:
				NR = 1
				ressults = []
				to_search = []

				#make a happy little list
				for sugg in list:
					if sugg.lower() != thing.lower():
						to_search.append(sugg)
						ressults.append("{0} {1}".format(wiki.get_keycap(NR),sugg))
						NR = NR + 1
					else:
						pass

				#put stuff together

				if or_that != None:
					Maybe = "\n:zero: Or do you mean: `" + or_that + "`?"
				else:
					Maybe = ""
				base = ":mag_right: What exactly are you looking for?\n\n{0}\n{1}".format("\n".join(f for f in ressults), Maybe)

				#send question and get more stuff
				msg = await BASE.phaaze.send_message(message.channel, base)

				def sure(m):
					try:
						nr = int(m.content)
						return 10 >= nr > -1

					except:
						return False

				#choose a thing
				choose = await BASE.phaaze.wait_for_message(timeout=30, author=message.author, channel=message.channel, check=sure)

				#work on result
				if not choose == None:
					#change lang?
					if len(lang) > 1:
						wikipedia.set_lang(lang[1])
					else:
						wikipedia.set_lang("en")

					#select and request page
					file = int(choose.content) - 1

					if file > len(list) - 1:
						return

					if file != -1:
						try:
							page = wikipedia.page(to_search[file])
						except:
							return await BASE.phaaze.send_message(message.channel, ":warning: Sorry, but an unknown Error just broke the internet, try something else")
					else:
						page = wikipedia.page(or_that)

					#short it
					text = page.summary[:1900]
					if len(page.summary) > 1900: text = text + ". . . . . :bookmark_tabs: And more."

					#aaaand finished
					send = ":books: **{0}**\n\n{1}".format(page.title,text)
					return await BASE.phaaze.edit_message(msg, new_content=send, embed=None)

	def get_keycap(n):
		if n == 0:
			return ":zero:"
		if n == 1:
			return ":one:"
		if n == 2:
			return ":two:"
		if n == 3:
			return ":three:"
		if n == 4:
			return ":four:"
		if n == 5:
			return ":five:"
		if n == 6:
			return ":six:"
		if n == 7:
			return ":seven:"
		if n == 8:
			return ":eight:"
		if n == 9:
			return ":nine:"
		if n == 10:
			return ":keycap_ten:"
		if n > 10:
			return ":arrow_forward:"

class whois(object):
	temp = re.compile(r'.*#[0-9]{4}')

	async def whois(BASE, message):
		m = message.content.split(" ")

		#by_myself
		if len(m) == 1:
			return await whois.finish(BASE, message, message.author)

		#by_mention
		if len(message.mentions) >= 1:
			if len(message.mentions) > 1:
				return await BASE.phaaze.send_message(message.channel, ":warning: You can not mention multiple members, only 1.")
			if not message.mentions[0].id in m[1]:
				return await BASE.phaaze.send_message(message.channel, ":warning: The Member mention must be on first place")

			return await whois.finish(BASE, message, message.mentions[0])

		#contains a role
		if len(message.role_mentions) > 0:
			return await BASE.phaaze.send_message(message.channel, ":warning: Whois dosn't support roles.")

		#by_id
		elif m[1].isdigit() and len(m) == 2:
			b = await whois.get_by_id(BASE, message, m[1])
			if b is None: return await BASE.phaaze.send_message(message.channel, ":warning: The ID search didn't find anything.")
			return await whois.finish(BASE, message, b)

		#by_name
		else:
			b = await whois.get_by_name(BASE, message, m[1:])
			if b is None: return await BASE.phaaze.send_message(message.channel, ":warning: The Name search didn't find anything.")
			return await whois.finish(BASE, message, b)

	async def get_by_id(BASE, message, number):
		user = discord.utils.get(message.server.members, id=number)
		return user

	async def get_by_name(BASE, message, name):
		name = " ".join(d for d in name)
		user = discord.utils.get(message.server.members, name=name)
		return user

	async def finish(BASE, message, user):
		if user.nick is not None:
			user.nick = "Nickname: " + user.nick
		else: user.nick == None
		if str(user.status) == "online": status = "Online"
		elif str(user.status) == "offline": status = "Offline"
		elif str(user.status) == "idle": status = "AFK"
		elif str(user.status) == "dnd": status = "Do not disturb"
		else: status = "Unknown"

		role_list = []
		for role in sorted(user.roles, key=lambda role: role.position, reverse=True):
			if role.name != "@everyone":
				role_list.append([role.position, role.name])

		now = datetime.datetime.now()
		cr = user.created_at
		jo = user.joined_at
		formated_created = "{t_} *[{delta} days ago]*".format(
															t_ = cr.strftime("%d.%m.%y (%H:%M)"),
															delta = (now - cr).days)

		formated_joined = "{t_} *[{delta} days ago]*".format(
															t_ = jo.strftime("%d.%m.%y (%H:%M)"),
															delta = (now - jo).days)

		main = 	"**ID**: {0}\n"\
				"**Discriminator**: {1}\n"\
				"**Acc. created at**: {2}\n"\
				"**Joined at**: {3}".format(user.id,
											user.discriminator,
											formated_created,
											formated_joined)

		tem = discord.Embed (
			title=user.nick,
			color=user.colour.value,
			description=main)

		if user.bot: tem.add_field(name=":robot: Bot-account:",value="True",inline=True)

		if not user.game == None:
			if user.game.type == 1:
				tem.add_field(name=":video_camera: Currently Streaming:",value=user.game.name,inline=True)
			else:
				tem.add_field(name=":game_die: Playing:",value=user.game.name,inline=True)
		tem.add_field(name=":satellite: Status:",value=status,inline=True)

		if len(role_list) >= 1:
			tem.add_field(name=":notepad_spiral: Roles:",value="```" + tabulate(role_list, tablefmt="plain") + "```",inline=False)
		else:
			tem.add_field(name=":notepad_spiral: Roles:",value="None",inline=False)

		tem.set_author(name="Name: {0}".format(user.name))

		if user.avatar_url != "": tem.set_image(url=user.avatar_url)
		else: tem.set_image(url=user.default_avatar_url)

		return await BASE.phaaze.send_message(message.channel, content=message.author.mention, embed=tem)
