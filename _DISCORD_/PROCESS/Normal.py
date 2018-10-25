#BASE.modules._Discord_.PROCESS.Normal

import asyncio, requests, discord, random, re, datetime
from tabulate import tabulate

class Forbidden(object):
	async def disable_chan_quote(BASE, message, kwargs):
		m = await BASE.discord.send_message(message.channel, ":no_entry_sign: Quote ask is disabled for this channel, only Mods and the Serverowner can use them.")
		await asyncio.sleep(2.5)
		await BASE.discord.delete_message(m)

	async def owner_disabled_quote(BASE, message, kwargs):
		m = await BASE.discord.send_message(message.channel, ":no_entry_sign: The Serverowner disabled Quotes, only the Serverowner can use them.")
		await asyncio.sleep(2.5)
		await BASE.discord.delete_message(m)

class Everything(object):
	async def emotes(BASE, message, kwargs):
		server_emotes = [e for e in message.server.emojis if not e.managed]
		server_emotes_managed = [e for e in message.server.emojis if e.managed]

		if not server_emotes and not server_emotes_managed:
			return await BASE.discord.send_message(message.channel, ":x: This Server has no Emotes at all")

		if server_emotes:
			e_ = " | ".join(str(e) + " - `" + e.name + "`" for e in sorted(server_emotes, key=lambda e: e.name))
			server_emotes = f"Server Custom Emotes: **{str(len(server_emotes))}**\n\n{e_}\n"

		else: server_emotes = ""

		if server_emotes_managed:
			e_ = " | ".join("`" + e.name + "`" for e in sorted(server_emotes_managed, key=lambda e: e.name))
			server_emotes_managed = f"\nTwitch Integration Emotes: **{str(len(server_emotes_managed))}**\n\n{e_}"

		else: server_emotes_managed = ""

		x = "\n\nThere are to many Emotes to display all"
		rep_message = server_emotes + server_emotes_managed
		if len(rep_message) > 1999:
			rep_message[:(1999-len(x))] + x

		return await BASE.discord.send_message(message.channel, rep_message[:1999])

	async def define(BASE, message, kwargs):
		LINK = "https://mashape-community-urban-dictionary.p.mashape.com/define"
		TERM = "?term="
		Header = {'X-Mashape-Key': BASE.access.Mashape}

		m = message.content[(len(BASE.vars.TRIGGER_DISCORD)):].split(" ")

		if len(m) == 1:
			return await BASE.discord.send_message(message.channel, f':warning: You need to define a word. `{BASE.vars.TRIGGER_DISCORD}define [thing]`')

		thing = " ".join(g for g in m[1:])

		if "phaaze" in message.content.lower() or "phaazebot" in message.content.lower():
			# REEEEEEE
			return await BASE.discord.send_message(message.channel, "Thats me :D")

		#request or end
		try:
			res = requests.get(LINK+TERM+thing, headers= Header).json()
		except:
			return await BASE.discord.send_message(message.channel, ":warning: A Error occurred during your requestyour request, try agoin later")

		if not res.get("list", []):
			return await BASE.discord.send_message(message.channel, f":x: Sorry, but Urban dictionary don't know what: `{thing}` is")

		top = res.get("list", [])[0].get("definition", "[N/A]")
		example = res.get("list", [])[0].get("example", "[N/A]")

		rest_list = res["list"][1:]

		emb = discord.Embed(description=":notebook_with_decorative_cover:\n"+top)
		emb.set_author(name=thing, url="http://www.urbandictionary.com/define.php?term="+thing.replace(" ", "+"))
		emb.add_field(name=":book: Example", value=example)
		if rest_list: emb.set_footer(text=f"and {str(len(rest_list))} other definitions")

		return await BASE.discord.send_message(message.channel, embed=emb)

	async def choice(BASE, message, kwargs):
		m = message.content[(len(BASE.vars.TRIGGER_DISCORD)):].split(" ")
		if len(m) == 1:
			return await BASE.discord.send_message(message.channel, ":warning: Missing arguments, at least 2 options separated by \";\" are needed")

		M = message.content[(len(BASE.vars.TRIGGER_DISCORD)):].split(" ", 1)[1].split(";")

		for item in M:
			item.replace(" ","")
			item.replace("	","")

		try:
			M.remove("")
		except:
			pass

		if len(M) == 1:
			return await BASE.discord.send_message(message.channel, ":warning: Missing arguments, at least 2 options separated by \";\" are needed")

		winner = random.choice(M)
		winner = winner.replace("`", "")
		winner = winner.replace("@everyone", "")
		winner = winner.replace("**", "")

		resp = "And the winner is...\n\n:game_die:- **{}** -:8ball:".format(winner)

		return await BASE.discord.send_message(message.channel, resp)

class Whois(object):

	async def Base(BASE, message, kwargs):
		m = message.content[(len(BASE.vars.TRIGGER_DISCORD)):].split(" ")

		#by_myself
		if len(m) == 1:
			return await Whois.finish(BASE, message, kwargs, message.author)

		#by_mention
		if message.mentions:
			return await Whois.finish(BASE, message, kwargs, message.mentions[0])

		#by_id
		elif m[1].isdigit():
			user = discord.utils.get(message.server.members, id=m[1])
			if user is None:
				return await BASE.discord.send_message(message.channel, f":warning: No user found with ID: {m[1]}")

			return await Whois.finish(BASE, message, kwargs, user)

		#by_name
		else:
			name = " ".join(s for s in m[1:])
			user = discord.utils.get(message.server.members, name=name)
			if user is None:
				return await BASE.discord.send_message(message.channel, f":warning: No user found with Name: `{name}`")

			return await Whois.finish(BASE, message, kwargs, user)

	async def finish(BASE, message, kwargs, user):
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

		main = 	f"**ID**: {user.id}\n"\
				f"**Discriminator**: {user.discriminator}\n"\
				f"**Acc. created at**: {formated_created}\n"\
				f"**Joined at**: {formated_joined}"

		tem = discord.Embed (
			title=user.nick,
			color=user.colour.value,
			description=main)

		if user.bot:
			tem.add_field(name=":robot: Bot-account:",value="True",inline=True)

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

		if user.avatar_url != "":
			tem.set_image(url=user.avatar_url)
		else:
			tem.set_image(url=user.default_avatar_url)

		return await BASE.discord.send_message(message.channel, embed=tem)

class Quotes(object):
	async def Base(BASE, message, kwargs):
		if kwargs.get('server_setting', {}).get('owner_disable_quote', False) and not await BASE.modules._Discord_.Utils.is_Owner(BASE, message):
			asyncio.ensure_future(Forbidden.owner_disabled_quote(BASE, message, kwargs))
			return
		if message.channel.id in kwargs.get('server_setting', {}).get('disable_chan_quote', []) and not await BASE.modules._Discord_.Utils.is_Mod(BASE, message):
			asyncio.ensure_future(Forbidden.disable_chan_quote(BASE, message, kwargs))
			return

		m = message.content[(len(BASE.vars.TRIGGER_DISCORD)):].split(' ')
		server_quotes = kwargs.get('server_quotes', {})

		if not server_quotes:
			return await BASE.discord.send_message(message.channel, ":grey_exclamation: This server don't has any Quotes")

		if len(m) == 1:
			quote = random.choice(server_quotes)
			en = discord.Embed(description=quote.get('content', '[ERROR GETTING QUOTE INFO]'))
			en.set_footer(text="ID: "+str(quote.get('id', '[N/A]')))
			return await BASE.discord.send_message(message.channel, embed=en)

		if not m[1].isdigit():
			return await BASE.discord.send_message(message.channel, ":warning: If you want to get a specific quote use a number")

		index = int(m[1])

		for quote in server_quotes:
			if quote.get('id', None) == index:
				en = discord.Embed(description=quote.get('content', '[ERROR GETTING QUOTE INFO]'))
				en.set_footer(text="ID: "+str(quote.get('id', '[N/A]')))
				return await BASE.discord.send_message(message.channel, embed=en)

		return await BASE.discord.send_message(message.channel, f":warning: No quote found with id {index}")

class Wiki(object):

	SEARCH = "https://{}.wikipedia.org/w/api.php?action=opensearch&limit=7&search="
	SUMMARY = "https://{}.wikipedia.org/api/rest_v1/page/summary/"
	WIKI_SEARCH_COOLDOWN = []

	async def Base(BASE, message, kwargs):
		if message.author.id not in Wiki.WIKI_SEARCH_COOLDOWN:
			asyncio.ensure_future(Wiki.cooldown(message))
		else: return

		m = message.content[(len(BASE.vars.TRIGGER_DISCORD)):].split()

		if len(m) == 1:
			return await BASE.discord.send_message(message.channel, f":warning: You need to define something you wanna search for. `{BASE.vars.TRIGGER_DISCORD}wiki(/Language) [thing]"\
			f"`\n\n`(/Language)` - (Optional) change the return language e.g. `{BASE.vars.TRIGGER_DISCORD}wiki/de YouTube` return German results | Default: en\n`[thing]` - whatever you wanna look up.")

		language = Wiki.get_language(m[0])
		thing = " ".join(w for w in m[1:])

		try:
			r = requests.get( Wiki.SEARCH.format(language)+thing ).json()
		except:
			return await BASE.discord.send_message(message.channel, f":warning: Could not connect to Wikipedia, maybe the language you (`{language}`) entered is not avaliable?.")

		r = Wiki.remove_refereTo(r)

		if not r[1]:
			return await BASE.discord.send_message(
				message.channel, f":x: Wikipedia could not found anything for `{thing}` , try again in a moment.")

		if len(r[1]) == 1:
			return await Wiki.get_summary(BASE, message, kwargs, language, r[1][0])

		if r[0].lower() in [t.lower() for t in r[1]]:
			return await Wiki.get_summary(BASE, message, kwargs, language, r[0])

		else:
			return await Wiki.get_autocomplete(BASE, message, kwargs, language, r)

	async def get_autocomplete(BASE, message, kwargs, language, r):
		rText = ""
		n = 1
		for element in r[1]:
			rText += f"{Wiki.get_number(n)} {element}\n"
			n += 1
		emb = discord.Embed(title=":grey_exclamation: There are multiple results. Please choose", description=rText)
		emb.set_footer(text="Please type only the number you wanna search.")
		emb.set_footer(text="Provided by Wikipedia", icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Wikipedia-logo-v2.svg/2000px-Wikipedia-logo-v2.svg.png")

		x = await BASE.discord.send_message(message.channel, embed=emb)
		a = await BASE.discord.wait_for_message(timeout=15, author=message.author, channel=message.channel)
		if not a.content.lower().isdigit():
			await BASE.discord.delete_message(x)
			return await BASE.discord.send_message(message.channel, ":warning: Please only enter a number... Try later again")

		elif not (0 < int(a.content) <= len(r[1])):
			await BASE.discord.delete_message(x)
			return await BASE.discord.send_message(message.channel, f":warning: Please only enter a number between 1 - {str(len(r[1]))}... Try later again")

		else:
			return await Wiki.get_summary(BASE, message, kwargs, language, r[1][(int(a.content)-1)])

	async def get_summary(BASE, message, kwargs, language, therm):
		FAIL = '[ERROR REQUEST]'
		r = requests.get( Wiki.SUMMARY.format(language)+therm ).json()

		emb = discord.Embed(title=r.get('description', None) ,description=r.get('extract', FAIL), url=r.get('content_urls', {}).get('desktop', {}).get('page', ""))
		emb.set_author(name=r.get('title', FAIL), url=r.get('content_urls', {}).get('desktop', {}).get('page', ""))
		emb.set_thumbnail(url=r.get('thumbnail', {}).get('source', ''))
		emb.set_footer(text="Provided by Wikipedia", icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Wikipedia-logo-v2.svg/2000px-Wikipedia-logo-v2.svg.png")
		return await BASE.discord.send_message(message.channel, embed=emb)

	def get_language(str_):
		spl = str_.split('/')
		if len(spl) >= 2:
			return spl[1]
		else:
			return "en"

	def get_number(number):
		if number == 1:
			return ":one: "

		if number == 2:
			return ":two: "

		if number == 3:
			return ":three: "

		if number == 4:
			return ":four: "

		if number == 5:
			return ":five: "

		if number == 6:
			return ":six: "

		if number == 7:
			return ":seven: "

	def remove_refereTo(r):
		try:
			if r[2][0].lower().endswith(":") or r[2][0].lower() == "":
				r[1].pop(0)
				r[2].pop(0)
		except: pass

		return r

	async def cooldown(m):
		Wiki.WIKI_SEARCH_COOLDOWN.append(m.author.id)
		await asyncio.sleep(15)
		try:
			Wiki.WIKI_SEARCH_COOLDOWN.remove(m.author.id)
		except:
			pass

class Osu(object):
	async def Base(BASE, message, kwargs):

		m = message.content[(len(BASE.vars.TRIGGER_DISCORD)):].lower().split(" ")

		if len(m) == 1:
			return await BASE.discord.send_message(
				message.channel,
				f":warning: Missing a option!  Usage: `{BASE.vars.TRIGGER_DISCORD}osu [Option]`\n\n"\
				f"Available options: `stats`, `map`, `calc`")

		elif len(m) >= 2:

			if m[1].startswith("stats"):
				return await Osu.stats(BASE, message, kwargs)

			elif m[1].startswith("map"):
				# TODO: Fix map stats for new osu design
				if len(m) == 2:
					return await BASE.discord.send_message(message.channel, ":warning: Missing Map Link!  Usage: `{0}osu map [map/mapset/mapcreator - LINK]`".format(BASE.vars.TRIGGER_DISCORD))

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
					return await BASE.discord.send_message(message.channel, ":warning: Invalid or missing Link!  Usage: `{0}osu map [map/mapset/mapcreator - LINK]`".format(BASE.vars.TRIGGER_DISCORD))

				#get set/map/creator
				stuff = await BASE.modules.osu.get_all_maps(BASE, ID=search_id, mode=mode)
				if stuff == None and mode == "u": return await BASE.discord.send_message(message.channel, ":warning: The user does not exist or dosn't created any beatmaps".format(BASE.vars.TRIGGER_DISCORD))
				if stuff == None: return await BASE.discord.send_message(message.channel, ":warning: Invalid or missing Link!  Usage: `{0}osu map [map/mapset/mapcreator - LINK]`".format(BASE.vars.TRIGGER_DISCORD))

				#one
				if mode == "b" or mode == "s" and len(stuff.all_maps) == 1: #one map
					beatmap = stuff.all_maps[0]
					meep = 	"mapped by {creator}\n\n"\
							"{symbol} **{approved_name}** | :green_heart: Favourite: **{favo}** {source}\n"\
							":star:: **{diff}** | :notes: BPM: **{bpm}** | :stopwatch: Lenght: **{full}** *(Drain: {drain})*\n"\
							":small_red_triangle:CS: {cs} | :small_red_triangle:AR: {ar} | :small_red_triangle:OD: {od} | :small_red_triangle:HP: {hp}\n"\
							"*MapID: {mID} | SetID: {sID}*".format	(
										symbol = await BASE.modules.Utils.get_osu_status_symbol(beatmap.approved),
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

					pp_100 = await BASE.modules.osu_utils.get_pp(beatmap.Map_ID, acc=100.0)
					pp_99 = await BASE.modules.osu_utils.get_pp(beatmap.Map_ID, acc=99.0)
					pp_98 = await BASE.modules.osu_utils.get_pp(beatmap.Map_ID, acc=98.0)

					osu_aw.add_field(name="PPcalc:",value="{pp_100}pp for 100% | {pp_99}pp for 99% | {pp_98}pp for 98%...\n`{TRIGGER_DISCORD}osu calc [maplink] (options)`".format	(
																																										TRIGGER_DISCORD = BASE.vars.TRIGGER_DISCORD,
																																										pp_100 = str(round(float(pp_100.pp), 2)),
																																										pp_99 = str(round(float(pp_99.pp), 2)),
																																										pp_98 = str(round(float(pp_98.pp), 2))

																																											), inline=True)

					if not beatmap.tags == []:
						osu_aw.add_field(name="Tags:",value=", ".join(tag for tag in beatmap.tags), inline=True)

					return await BASE.discord.send_message(message.channel, embed=osu_aw)


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
												symbol = await BASE.modules.Utils.get_osu_status_symbol(base_infos.approved),
												approved_name = base_infos.approved_name,
												artist = base_infos.artist,
												title = base_infos.title,
												diff_list = tabulate(listi, tablefmt="plain"),
												bpm = str(round(base_infos.bpm)))

					ggt = discord.Embed(title="Check it out", url="https://osu.ppy.sh/s/{0}".format(base_infos.Set_ID), color=int(0xFF69B4))

					if len(fff) > 1997: fff = ":no_entry_sign: Seems like this Mapset has to many diffs, its to much for the Discord message limit, sorry."

					return await BASE.discord.send_message(message.channel, content=fff, embed=ggt)


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
																														symbol = await BASE.modules.Utils.get_osu_status_symbol(_set[0].approved),
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

					await BASE.discord.send_message(message.channel, content=base_res, embed=ebb)
					try: await BASE.discord.delete_message(message)
					except: pass
					return

			#elif m[1].startswith("track"):
			#	return await BASE.discord.send_message(message.channel, ':cold_sweat: Sorry but the "track" modul is under construction! SOON:tm:')

			elif m[1].startswith("calc"):
				await BASE.modules.osu.pp_calc_for_maps(BASE, message)

			else:
				return await BASE.discord.send_message(message.channel, ":warning: `{0}` is not a option!  Available options: `stats`,`map` and `track`".format(m[1]))

	async def stats(BASE, message, kwargs):
		m = message.content[(len(BASE.vars.TRIGGER_DISCORD)):].split(" ")

		if len(m) == 2:
			return await BASE.discord.send_message(
				message.channel,
				f":warning: Missing User!\nUsage: `{BASE.vars.TRIGGER_DISCORD}osu stats(mode) [User]`\n"\
				f'`(mode)` - Optional: Can be empty, `/osu`, `/ctb`, `/mania` or `/taiko`\n'\
				f'`[User]` - osu link, name or id')

		c = m[1].split("/")
		try: mode = c[1]
		except: mode = "osu"

		#set mode
		if mode == "osu": MODE = "0"
		elif mode == "taiko": MODE = "1"
		elif mode == "ctb": MODE = "2"
		elif mode == "mania": MODE = "3"
		elif mode == "":
			return await BASE.discord.send_message(message.channel, ":warning: Option after `stats/` is missing. Available Options are: `osu, ctb ,mania ,taiko`  Or leave it free and remove the `/`.")
		else:
			return await BASE.discord.send_message(message.channel, ":warning: `{0}` is not a gamemode, Available are: `osu`,`ctb`,`mania`,`taiko`".format(c[1]))

		user_info, type_ = Osu.extract_user(" ".join(c for c in m[2:]))

		User = await BASE.modules._Osu_.Utils.get_user(BASE, u=user_info, m=MODE, t=type_)
		if User == None:
			return await BASE.discord.send_message(message.channel, ":warning: The given User could not found!")

		# Format the shit out of it :D

		pp = "{:,}".format(round(float(User.get('pp_raw', "0")), 2)) if User.get('pp_raw', None) != None else "-∞"
		acc = str(round(float(User.get('accuracy', None)), 2)) if User.get('accuracy', None) != None else "-∞"
		level = str(round(float(User.get('level', None)), 1)) if User.get('level', None) != None else "N/A"
		playcount = "{:,}".format(int(User.get('playcount', None))) if User.get('playcount', None) != None else "N/A"
		ranked_score = "{:,}".format(int(User.get('ranked_score', None))) if User.get('ranked_score', None) != None else "-∞"
		total_score = "{:,}".format(int(User.get('total_score',None))) if User.get('total_score', None) != None else "-∞"
		rank = "{:,}".format(int(User.get('pp_rank', None))) if User.get('pp_rank', None) != None else "-∞"
		country_rank = "{:,}".format(int(User.get('pp_country_rank', None))) if User.get('pp_country_rank', None) != None else "-∞"

		rtext = f":globe_with_meridians: #{rank}  |  :flag_{User.get('country','EU').lower()}: #{country_rank}\n"\
				f":part_alternation_mark: {pp} pp\n"\
				f":dart: {acc}% Accuracy\n"\
				f":military_medal: Level: {level}\n"\
				f":timer: Playcount: {playcount}\n"\
				f":chart_with_upwards_trend: Ranked Score: {ranked_score}\n"\
				f":card_box: Total Score: {total_score}\n"\
				f":id: {User.get('user_id', 'N/A')}"

		EMB = discord.Embed(
			title=User.get('username','[N/A]'),
			url="https://osu.ppy.sh/users/"+User.get('user_id', "3"),
			color=int(0xFF69B4),
			description=rtext
			)

		def none_is_zero(s):
			if s == None: return "0"
			return s

		table_R = 	[
						["A:", "{:,}".format(int(none_is_zero(User.get('count_rank_a', 0))))],
						["S:", "{:,}".format(int(none_is_zero(User.get('count_rank_s', 0))))],
						["SS:", "{:,}".format(int(none_is_zero(User.get('count_rank_ss', 0))))],
						["SX:", "{:,}".format(int(none_is_zero(User.get('count_rank_sh', 0))))],
						["SSX:", "{:,}".format(int(none_is_zero(User.get('count_rank_ssh', 0))))],
					]

		EMB.add_field(name="Ranks:",value="```{}```".format(tabulate(table_R, tablefmt="plain")), inline=True)

		EMB.set_thumbnail(url="https://a.ppy.sh/{0}".format(User.get('user_id', '3')))
		EMB.set_footer(text="Provided by osu!", icon_url="http://w.ppy.sh/c/c9/Logo.png")
		EMB.set_author(name="Stats for: {0}".format(mode.lower().capitalize()))

		return await BASE.discord.send_message(message.channel, embed=EMB)

	def extract_user(str_):
		#link
		u = re.match(r'https://osu\.ppy\.sh/(users|u)/(.+)', str_)
		t = "string"
		if u != None:
			u = u.group(2)
			if u.isdigit():
				t = "id"

			return u , t

		if str_.isdigit():
			t = "id"

		return str_, t

class Giverole(object):

	async def Base(BASE, message, kwargs):
		m = message.content[(len(BASE.vars.TRIGGER_DISCORD)):].split(" ")

		if m[0].lower().endswith('-list'):
			return await Giverole.list_entrys(BASE, message, kwargs)

		if len(m) == 1:
			return await BASE.discord.send_message(message.channel, ":warning: Please add a key for the role you want")

		trigger = m[1]

		me = await BASE.modules._Discord_.Utils.return_real_me(BASE, message)

		if not me.server_permissions.manage_roles:
			return await BASE.discord.send_message(
				message.channel,
				":no_entry_sign: Phaaze don't has a role with the `Manage Roles` Permission."
			)

		r_id = None
		add_rolelist = await BASE.modules._Discord_.Utils.get_server_addrolelist(BASE, message.server.id)
		for role in add_rolelist:
			if role.get('trigger', '').lower() == trigger.lower():
				r_id = role.get('role_id', None)
				break

		server_role = discord.utils.get(message.server.roles, id=r_id)

		if server_role == None:
			return await BASE.discord.send_message(message.channel, f":warning: No giverole found with trigger: {trigger}")

		if me.top_role < server_role:
			return await BASE.discord.send_message(
				message.channel,
				":no_entry_sign: The Role: `{0}` is to high. Phaaze highest role has to be higher in hierarchy then: `{0}`".format(role.name.replace("`","´")))

		if server_role not in message.author.roles: #add
			await BASE.discord.add_roles(message.author, server_role)
			return await BASE.discord.send_message(message.channel, f":white_check_mark: successfull added you the role: '{server_role.name}'")
		else:
			await BASE.discord.remove_roles(message.author, server_role)
			return await BASE.discord.send_message(message.channel, f":white_check_mark: successfull removed '{server_role.name}' from you.")

	async def list_entrys(BASE, message, kwargs):
		addrolelist = await BASE.modules._Discord_.Utils.get_server_addrolelist(BASE, message.server.id, prevent_new=True)
		role_list = [ ['Trigger', 'linked with:'], ['',''] ]

		for r in addrolelist:
			role = discord.utils.get(message.server.roles, id=r.get('role_id', '0'))
			if role == None:
				role_name = "[DELETED ROLE]"
			else:
				role_name = role.name
			l = [r.get('trigger', '[N/A]'), role_name]

			role_list.append(l)

		table = tabulate(role_list, tablefmt="plain")

		return await BASE.discord.send_message(message.channel, f"All Give/Take -roles: \n\n```{table}```")

#Currently unusable D:
class Doujin(object):

	def __init__(self, BASE, message, kwargs):
		self.BASE = BASE
		self.message = message
		self.kwargs = kwargs

		self.parameter = {}
		pass

	async def api_error_message(self):
		I = await self.BASE.discord.send_message(
			self.message.channel,
			content=None,
			embed=discord.Embed(
				title=":octagonal_sign: Tsumino API is currently down, during website restructore",
				color=int(0xFF0000),
				description="'>doujin' and all subcommands won't work for now.\nTry later again..."
			))
		await asyncio.sleep(15)
		await self.BASE.discord.delete_message(I)

	async def Base(self):
		M = self.message.content.replace("\n", " ")
		m = M.lower()

		return await self.api_error_message()

		if 	re.search(r"^.doujin ?<?$", m):
			return await self.errors.no_options(self)

		if 	re.search(r"^.doujin <?help$", m):
			return await self._help()

		if 	re.search(r"^.doujin <?r(andom)?$", m):
			return await self.Tsumino_call()

		#parse all
		return await self.parse()

	async def parse(self):
		m = self.message.content.split("<")
		#remove command tirgger
		m.remove(m[0])

		if len(m) == 0:
			return await self.errors.no_options(self)

		for term in m:
			term = term.split(" ")
			try:
				term.remove("")
			except:
				pass

			#include add
			if re.search(r"^i(_t(ags?)?|t(ags?)?)?$", term[0]):

				option = term[0]
				term.remove(term[0])

				if len(term) == 0:
					return await self.errors.missing_value(self, option, "Included")
				else:
					self.parameter["TagInclude"] = [t for t in term]

			#exclude tag
			elif re.search(r"^e(_t(ags?)?|t(ags?)?)?$", term[0]):

				option = term[0]
				term.remove(term[0])

				if len(term) == 0:
					return await self.errors.missing_value(self, option, "Excluded")
				else:
					self.parameter["TagExclude"] = [t for t in term]

			#page min
			elif re.search(r"^(p|page)_?min(imum)?$", term[0]):

				option = term[0]
				term.remove(term[0])

				if len(term) == 0:
					return await self.errors.missing_value(self, option, "Page Minimum")

				elif len(term) > 1:
					return await self.errors.too_many_inputs(self, option, "Page Minimum")

				if not term[0].isdigit():
					return await self.errors.wrong_type(self, option, "Page Minimum", "Number")

				else:
					self.parameter["PageMinimum"] = [term[0]]

			#page max
			elif re.search(r"^(p|page)_?max(imum)?$", term[0]):

				option = term[0]
				term.remove(term[0])

				if len(term) == 0:
					return await self.errors.missing_value(self, option, "Page Maximum")

				elif len(term) > 1:
					return await self.errors.too_many_inputs(self, option, "Page Maximum")

				if not term[0].isdigit():
					return await self.errors.wrong_type(self, option, "Page Maximum", "Number")

				else:
					self.parameter["PageMaximum"] = [term[0]]

			#stars
			elif re.search(r"^s(tars?)?$", term[0]):

				option = term[0]
				term.remove(term[0])

				if len(term) == 0:
					return await self.errors.missing_value(self, option, "Star Rating")

				elif len(term) > 1:
					return await self.errors.too_many_inputs(self, option, "Star Rating")

				if not term[0].isdigit():
					return await self.errors.wrong_type(self, option, "Star Rating", "Number")

				if not re.search(r"^[0-5]$", term[0]):
					return await self.errors.too_high(self, option, "Star")

				else:
					self.parameter["RateMinimum"] = [term[0]]

			#anime
			elif re.search(r"^a(nimes?)?$", term[0]):

				option = term[0]
				term.remove(term[0])

				if len(term) == 0:
					return await self.errors.missing_value(self, option, "Anime")

				formated = []
				anime_hits = 0
				for value in term:
					animes = requests.get("http://tsumino.com/api/tag?term={0}".format(value.replace("_", "+")))
					for anime in animes.json()["Data"]:
						if anime["Type"] == 6:
							 anime_hits += 1
							 formated.append(anime["Name"])
							 break

					if anime_hits == 0:
						return await self.errors.non_found(self, option, "Anime", value)

				self.parameter["Parodies"] = formated

			#chars
			elif re.search(r"^c(hars?)?(acters?)?$", term[0]):

				option = term[0]
				term.remove(term[0])

				if len(term) == 0:
					return await self.errors.missing_value(self, option, "Character")

				formated = []
				anime_hits = 0
				for value in term:
					chars = requests.get("http://tsumino.com/api/tag?term={0}".format(value.replace("_", "+")))
					for char_ in chars.json()["Data"]:
						if char_["Type"] == 7:
							 anime_hits += 1
							 formated.append(char_["Name"])
							 break

					if anime_hits == 0:
						return await self.errors.non_found(self, option, "Character", value)

				self.parameter["Characters"] = formated

			#painter / artist
			elif re.search(r"^p(ainters?)?$", term[0]):

				option = term[0]
				term.remove(term[0])

				if len(term) == 0:
					return await self.errors.missing_value(self, option, "Artist")

				formated = []
				artist_hits = 0
				for value in term:
					artists = requests.get("http://tsumino.com/api/tag?term={0}".format(value.replace("_", "+")))
					for artist in artists.json()["Data"]:
						if artist["Type"] == 5:
							 artist_hits += 1
							 formated.append(artist["Name"])
							 break

					if artist_hits == 0:
						return await self.errors.non_found(self, option, "Artist", value)

								#Missing URL Prefix...
				self.parameter["Artist"] = formated

			#=
			elif re.search(r"^=", term[0]):

				option = term[0]
				term.remove(term[0])

				if len(term) == 0:
					return await self.errors.missing_value(self, option, "Raw Search")

				self.parameter["Search"] = [term[0]]

			#nothing
			else:
				return await self.errors.unknown(self, term[0])

		##nextup
		return await self.Tsumino_call()

	async def Tsumino_call(self):
		MAIN = "https://www.tsumino.com/api/book?SortOptions=Random"
		SEARCH = ""

		for term in self.parameter:
			SEARCH = SEARCH + "".join("&" + term + "=" + x.replace("_", "+") for x in self.parameter[term])

		site = requests.get(MAIN+SEARCH)
		search_return = site.json()
		return await self.format_and_send_message(search_return)

	async def format_and_send_message(self, result):
		if len(result["Data"]) == 0:
			return await self.errors.noting_found(self)

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

		dece = 	":page_facing_up: : {pages}     :star: : {stars}    :paintbrush: : {artist}"\
				"{animes}{chars}"\
				"\n:label: : {tags}".format(stars=stars, pages=pages, chars=chars, animes=animes, tags=tags, artist=artist)

		emb = discord.Embed(
						title=":diamond_shape_with_a_dot_inside:" +Book["Object"]["Title"],
						url=Book["Meta"]["Info"],
						colour=int(0x22a7f0),
						description=dece
						)
		emb.set_image(url=Book["Meta"]["Thumb"])
		emb.set_footer(text="Provided by Tsumino", icon_url="http://www.tsumino.com/content/res/logo.png")

		return await self.BASE.discord.send_message(self.message.channel, embed=emb)

	class errors:
		async def no_options(self):
			try:
				I = await self.BASE.discord.send_message(
					self.message.channel,
					content=None,
					embed=discord.Embed(
						title=":warning: Error: No Options",
						color=int(0xFF0000),
						description=
							"You need to define at least one option!\n"\
							"Use `{0}doujin help` for a list of all options.".format(self.BASE.vars.TRIGGER_DISCORD))
					)
				await asyncio.sleep(15)
				await self.BASE.discord.delete_message(I)
			except:
				pass

		async def missing_value(self, short_, long_):
			try:
				I = await self.BASE.discord.send_message(
					self.message.channel,
					content=None,
					embed=discord.Embed(
						title=":warning: Error: Missing value",
						color=int(0xFF0000),
						description=
							"**{1}** - *\"{2}\"* needs at least one value!\n"\
							"Use `{0}doujin help` for a list of all options.".format(self.BASE.vars.TRIGGER_DISCORD, short_, long_))
					)
				await asyncio.sleep(15)
				await self.BASE.discord.delete_message(I)
			except:
				pass

		async def too_high(self, short_, long_):
			try:
				I = await self.BASE.discord.send_message(
					self.message.channel,
					content=None,
					embed=discord.Embed(
						title=":warning: Error: Missing value",
						color=int(0xFF0000),
						description=
							"**{1}** - *\"{2}\"* only takes a value from 0-5\n"\
							"Use `{0}doujin help` for a list of all options.".format(self.BASE.vars.TRIGGER_DISCORD, short_, long_))
					)
				await asyncio.sleep(15)
				await self.BASE.discord.delete_message(I)
			except:
				pass

		async def too_many_inputs(self, short_, long_):
			try:
				I = await self.BASE.discord.send_message(
					self.message.channel,
					content=None,
					embed=discord.Embed(
						title=":warning: Error: Too many values",
						color=int(0xFF0000),
						description=
							"**{1}** - *\"{2}\"* only uses one value!\n"\
							"Use `{0}doujin help` for a list of all options.".format(self.BASE.vars.TRIGGER_DISCORD, short_, long_))
					)
				await asyncio.sleep(15)
				await self.BASE.discord.delete_message(I)
			except:
				pass

		async def wrong_type(self, short_, long_, type_):
			try:
				I = await self.BASE.discord.send_message(
					self.message.channel,
					content=None,
					embed=discord.Embed(
						title=":warning: Error: Wrong Type",
						color=int(0xFF0000),
						description=
							"**{1}** - *\"{2}\"* awaits a `{3}` value\n"\
							"Use `{0}doujin help` for a list of all options.".format(self.BASE.vars.TRIGGER_DISCORD, short_, long_, type_))
					)
				await asyncio.sleep(15)
				await self.BASE.discord.delete_message(I)
			except:
				pass

		async def non_found(self, short_, long_, values):
			try:
				I = await self.BASE.discord.send_message(
					self.message.channel,
					content=None,
					embed=discord.Embed(
						title=":warning: Error: Autocomplete failed",
						color=int(0xFF0000),
						description=
							"**{0}** - *\"{1}\" autocomplete* failed\n"\
							"`{2}` yield no ressults\n".format(short_, long_, values))
					)
				await asyncio.sleep(15)
				await self.BASE.discord.delete_message(I)
			except:
				pass

		async def unknown(self, value):
			try:
				I = await self.BASE.discord.send_message(
					self.message.channel,
					content=None,
					embed=discord.Embed(
						title=":warning: Error: Unknown option",
						color=int(0xFF0000),
						description=
							"**{1}** is a unknown option.\n"\
							"Use `{0}doujin help` for a list of all options.".format(self.BASE.vars.TRIGGER_DISCORD, value))
					)
				await asyncio.sleep(15)
				await self.BASE.discord.delete_message(I)
			except:
				pass

		async def noting_found(self):
			try:
				await self.BASE.discord.send_message(
					self.message.channel,
					content=None,
					embed=discord.Embed(
						title=":no_entry_sign: No Results",
						color=int(0xFF0000),
						description=
							"Your Search yield no results, try again")
					)
			except:
				pass

	async def _help(self):
		try:
			await self.BASE.discord.send_message(self.message.channel, ":incoming_envelope: --> PM")
		except:
			pass
		try:
			return await self.BASE.discord.send_message(self.message.author, "http://phaaze.wikia.com/wiki/Discord-Commands-Normal-doujin\n" + self.BASE.vars.doujin_help)
		except:
			pass
