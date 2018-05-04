#BASE.modules._Osu_.Utils

import asyncio, random, json,requests, os, discord, re
from UTILS import oppai as oppai

already_in_pairing_proccess = []

MAIN = "https://osu.ppy.sh/api/"
USER = "get_user"
MAP = "get_beatmaps"

class default_format(object):
	osu = "[[osu_link] [titel] [[version]]] ★ [stars] | Lenght: [lenght]min | BPM: [bpm] >> [requester]"
	osu_link_format = "http://osu.ppy.sh/b/[id]"
	twitch = "[titel] [[version]] by [creator] | ★ [stars] | Lenght: [lenght]min | BPM: [bpm]"

async def verify(BASE, message):
	m = message.content.split(" ")

	if len(m) == 1:
		confirm = await BASE.modules._Twitch_.Utils.get_opposite_osu_twitch(BASE, message.name, platform="osu")
		if confirm == None:
			if message.name in already_in_pairing_proccess:
				return await BASE.Osu_IRC.send_message(message.name, "You are already in a verify proccess. if you forgot your Number wait 5min and try it again.")
			pair_number = str(pairing_object(BASE, osu_name=message.name).verify)
			await BASE.Osu_IRC.send_message(message.name, "Your account is not paired to a Twitch.tv Channel | Enter '!osuverify {0}' in your Twitch channel to pair it. (you have 5min)".format(pair_number))
			already_in_pairing_proccess.append(message.name)

		else:
			await BASE.Osu_IRC.send_message(message.name, "Your account is paired! Twitch channel: {0} | Osu Account: {1}".format(confirm["twitch"]["name"], confirm["osu"]["name"]))
			await BASE.Osu_IRC.send_message(message.name, "Wanna break your connection? --> '!disconnect'")

	elif len(m) == 2:
		a_o = None
		for aouth_o in BASE.queue.twitch_osu_verify:
			if str(aouth_o.verify) == m[1]:
				a_o = aouth_o

		if a_o == None:
			await BASE.Osu_IRC.send_message(message.name, "{0} is not awaited for verify, be sure to don't make typos. (like i do all the time LUL)".format(m[1]))

		else:
			aouth_o.osu_name = message.name
			await BASE.Osu_IRC.send_message(message.name, "Your Osu name has been set. If everything is completed you will recive a message soon.")

async def download_map(ID):
	link = "https://osu.ppy.sh/osu/" + ID
	h = requests.get(link)
	file = open("UTILS/OSU_MAPS/"+ID+".osu", "wb")
	file.write(bytes(h.text, "UTF-8"))
	file.close()
	return "UTILS/OSU_MAPS/"+ID+".osu"

async def get_pp(ID, c100=0, c50=0, misses=0, sv=1, acc=100.0, combo=0, mod_s=""):
	path = await download_map(ID)

	e = oppai.calc(path, c100=c100, c50=c50, misses=misses, sv=sv, acc=acc, combo=combo, mod_s=mod_s)
	os.remove("UTILS/OSU_MAPS/"+ID+".osu")

	return e

async def get_user(BASE, u=None, m="0", t=None):
	if u == None: return None

	if t==None and u.isdigit():
		t="id"
	elif t==None and not u.isdigit():
		t="string"

	result = requests.get(f"{MAIN}{USER}?k={BASE.access.Osu_API_Token}&m={m}&type={t}&u={u}")
	result = result.json()

	#not found
	if result == []: return None

	return result[0]

async def get_all_maps(BASE, ID=None, mode="b"):
	KEY = "?k={0}".format(BASE.access.Osu_API_Token)

	if ID == None: return None

	#request stuff
	r_str = MAIN + MAP + KEY + "&{0}={1}".format(mode, ID)
	r = requests.get(r_str)
	r = r.json()

	#No result
	if r == []: return None

	def sort_in_mapsets(maps):
		if len(maps) == 1:
			return maps

		set_result = []

		Set_exist = []
		for map_ in maps:
			if not map_.Set_ID in Set_exist:
				Set_exist.append(map_.Set_ID)
				set_result.append([m for m in maps if m.Set_ID == map_.Set_ID])

			else: pass

		return set_result

	class map_object(object):
		def __init__(self, info):
			#4 = loved, 3 = qualified, 2 = approved, 1 = ranked, 0 = pending, -1 = WIP, -2 = graveyard
			if info["approved"] == "-2":
				self.approved = "-2"
				self.approved_name = "Graveyard"
			elif info["approved"] == "-1":
				self.approved = "-1"
				self.approved_name = "WIP"
			elif info["approved"] == "0":
				self.approved = "0"
				self.approved_name = "Pending"
			elif info["approved"] == "1":
				self.approved = "1"
				self.approved_name = "Ranked"
			elif info["approved"] == "2":
				self.approved = "2"
				self.approved_name = "Approved"
			elif info["approved"] == "3":
				self.approved = "3"
				self.approved_name = "Qualified"
			elif info["approved"] == "4":
				self.approved = "4"
				self.approved_name = "Loved"
			else:
				self.approved = None
				self.approved_name = None

			#meta
			self.Set_ID = info["beatmapset_id"]
			self.Map_ID = info["beatmap_id"]
			self.favos = info["favourite_count"]
			self.tags = info["tags"].split(" ")

			#infos
			self.version = info["version"]
			self.artist = info["artist"]
			self.title = info["title"]
			self.creator = info["creator"]
			self.source = info["source"]

			#diff
			self.diff = float(info["difficultyrating"])
			self.cs = float(info["diff_size"])
			self.od = float(info["diff_overall"])
			self.ar = float(info["diff_approach"])
			self.hp = float(info["diff_drain"])
			self.bpm = float(info["bpm"])

			#time
			F_minutes, F_seconds = divmod(int(info["total_length"]), 60)
			D_minutes, D_seconds = divmod(int(info["hit_length"]), 60)
			self.lenght = str(F_minutes) + "," + str(F_seconds if F_seconds >= 10 else "0" + str(F_seconds))
			self.drain = str(D_minutes) + "," + str(D_seconds if D_seconds >= 10 else "0" + str(D_seconds))

			#stuff
			self.playcount = info["playcount"]
			self.passcount = info["passcount"]

	class resullts(object):
		def __init__(self, resp):

			if mode == "b": mode_name = "Single_map"
			if mode == "s": mode_name = "Beatmap_set"
			if mode == "u": mode_name = "User_maps"

			self.result = resp
			self.mode = mode
			self.mode_name = mode_name

			#convert all things into objects
			self.all_maps = [map_object(map_) for map_ in resp]
			self.map_sets = sort_in_mapsets(self.all_maps)


	return resullts(r)

async def pp_calc_for_maps(BASE, message):
	m = message.content.split(" ")

	if len(m) == 2:
		return await BASE.discord.send_message(message.channel, ":warning: Missing Maplink (and options)\n\nOptions:\n`acc=[X]` - e.g. `acc=98,4` \n`combo=[X]` - e.g. `combo=1455` (0 == Full Combo)\n`miss=[X]` - e.g. `miss=4`\n`mods=[X]` - e.g. `mods=HDHR`\n\n**options seperated with Spaces**")

	if len(m) >= 3:
		def get_id_from_link(number):
			r = None
			try:
				if number.startswith("http"):
					link_parts = m[2].split("/b/")
					if link_parts[1].split("&")[0].isdigit():
						return link_parts[1]
				if number.isdigit():
					return number
			except:
				pass

			return r

		map_id_number = get_id_from_link(m[2])
		if "/s/" in m[2]:
			return await BASE.discord.send_message(message.channel, ":warning: PP Calc only works for single maps, not mapsets")
		if map_id_number == None:
			return await BASE.discord.send_message(message.channel, ":warning: Invalid Maplink. Only Map link or ID are vaild.")

	map_id_number = map_id_number.split("&")[0]

	miss_ = 0
	acc_ = 100.0
	combo_ = 0
	mods_ = ""

	#extrakt mods
	if len(m) >= 4:
		for option in m[3:]:
			if option.lower().startswith("acc="):
				try:
					v = float(option.split("=")[1])
					if not 0 < v < 100:
						return await BASE.discord.send_message(message.channel, ":warning: `acc` value has to be 0 < [X] <= 100.")
					acc_ = v
				except: return await BASE.discord.send_message(message.channel, ":warning: `acc` value can only be a *int* or *float*.")

			elif option.lower().startswith("combo="):
				try:
					v = int(option.split("=")[1])
					combo_ = v
				except: return await BASE.discord.send_message(message.channel, ":warning: `combo` value can only be a *int* from 0-[max_combo].")

			elif option.lower().startswith("miss="):
				try:
					v = int(option.split("=")[1])
					miss_ = v
				except: return await BASE.discord.send_message(message.channel, ":warning: `miss` value can only be a *int* from 0-[max_hit_obj].")

			elif option.lower().startswith("mods="):
				try:
					v = option.split("=")[1].upper()
					mods_ = v
				except: return await BASE.discord.send_message(message.channel, ":warning: Invaild syntax for `mods`.")

			else:
				return await BASE.discord.send_message(message.channel, ":warning: Invalid Option, `{0}` could not be processed, available are `mods`, `acc`, `combo` and `miss`".format(option))

	result = await BASE.modules.osu_utils.get_pp(map_id_number, acc=acc_, misses=miss_, combo=combo_, mod_s=mods_)

	osu_aw = discord.Embed	(	title = "{0}".format(result.version),
								description = "mabbed by: {0}".format(result.creator),
								color=int(0xFF69B4)
								)
	osu_aw.set_footer(text="Provided by osu!", icon_url="http://w.ppy.sh/c/c9/Logo.png")
	osu_aw.set_author(url="https://osu.ppy.sh/b/{0}".format(map_id_number) ,name="{0} - {1}".format(result.artist, result.title))
	h = "HP: **{0}** ▬ CS: **{1}** ▬ OD: **{2}** ▬ AR: **{3}**".format(str(round(result.hp)), str(round(result.cs)), str(round(result.od)), str(round(result.ar)))
	osu_aw.add_field(name="Diff.:",value=h, inline=False)
	moddds = mods_ if mods_ != "" else "NoMods"
	j = "{0}% - Combo: {5}/{2} - misses: {3} with {4}\nWhould give... : **{1}pp** 			*(+-2%)*".format(str(round(acc_)), str(round(result.pp, 1)), str(round(result.maxcombo)), str(miss_), moddds, str(combo_) if combo_ != 0 else str(round(result.maxcombo)))
	osu_aw.add_field(name="PP Calc.:",value=j, inline=False)

	return await BASE.discord.send_message(message.channel, embed=osu_aw)

async def twitch_osu(BASE, message):
	def get_link_out_of_content(content):
		m = content.lower()
		match = re.match(r'.+osu\.ppy\.sh\/(b|s|beatmapsets)\/(\d+)(/?#(\w+)?\/?(\d+)|)', m)

		r = {}
		r['set_'] = match.group(1)
		r['set_id_'] = match.group(2)
		r['mode_'] = match.group(4)
		r['map_id_'] = match.group(5)

		if r['map_id_'] == None:
			R_mode='s'
			r['map_id_'] = r['set_id_']
		else:
			R_mode='b'

		if r['mode_'] == "#osu": R_play = "0"
		elif r['mode_'] == "#taiko": R_play = "1"
		elif r['mode_'] == "#fruits": R_play = "2"
		elif r['mode_'] == "#mania": R_play = "3"
		else: R_play = "0"

		return r['map_id_']+"&m="+R_play, R_mode

	search_id, mode = get_link_out_of_content(message.content)

	osu_user = await BASE.modules._Twitch_.Utils.get_opposite_osu_twitch(BASE, message.room_id, platform="twitch")
	if osu_user == None: return

	osu_maps = await get_all_maps(BASE, ID=search_id, mode=mode)
	if osu_maps == None: return
	osu_map = osu_maps.all_maps[0]

	twitch_info_format = osu_user["twitch"].get("info_format", default_format.twitch)
	osu_info_format = osu_user["osu"].get("info_format", default_format.osu)

	#replace everything - Twitch
	twitch_info_format = twitch_info_format.replace("[titel]", str(osu_map.title))
	twitch_info_format = twitch_info_format.replace("[version]", str(osu_map.version))
	twitch_info_format = twitch_info_format.replace("[stars]", str(round(osu_map.diff,2)))
	twitch_info_format = twitch_info_format.replace("[lenght]", str(osu_map.lenght).replace(",",":"))
	twitch_info_format = twitch_info_format.replace("[bpm]", str(round(osu_map.bpm)))
	twitch_info_format = twitch_info_format.replace("[requester]", message.save_name)
	twitch_info_format = twitch_info_format.replace("[creator]", str(osu_map.creator))
	#replace everything - Osu
	osu_info_format = osu_info_format.replace("[titel]", str(osu_map.title))
	osu_info_format = osu_info_format.replace("[version]", str(osu_map.version))
	osu_info_format = osu_info_format.replace("[stars]", str(round(osu_map.diff,2)))
	osu_info_format = osu_info_format.replace("[lenght]", str(osu_map.lenght).replace(",",":"))
	osu_info_format = osu_info_format.replace("[bpm]", str(round(osu_map.bpm)))
	osu_info_format = osu_info_format.replace("[requester]", message.save_name)
	osu_info_format = osu_info_format.replace("[osu_link]", default_format.osu_link_format.replace("[id]", osu_map.Map_ID))

	await BASE.Twitch_IRC_connection.send_message(message.channel, twitch_info_format)
	await BASE.Osu_IRC.send_message(osu_user["osu"]["name"], osu_info_format)

class pairing_object(object):
	def __init__(self, BASE, osu_name=None, twitch_name=None, twitch_id=None):
		self.BASE = BASE
		self.osu_name = osu_name
		self.twitch_name = twitch_name
		self.twitch_id = twitch_id
		self.time = 300

		self.verify = random.randint(20000, 80000)
		self.BASE.queue.twitch_osu_verify.append(self)
		asyncio.ensure_future(self.time_left())

		async def time_left(self):
			while self.time != 0:
				self.time -= 5
				if self.osu_name != None and\
					self.twitch_name != None and\
					self.twitch_id != None:

					return await self.complete()

				await asyncio.sleep(5)

				await self.end()

				async def end(self):
					if self.twitch_id != None:
						self.BASE.modules._Twitch_.CMD.Mods.already_in_pairing_proccess.remove(self.twitch_id)

						if self.osu_name != None:
							self.BASE.modules._Osu_.Utils.already_in_pairing_proccess.remove(self.osu_name)

							self.BASE.queue.twitch_osu_verify.remove(self)

							async def complete(self):
								obj = dict()
								obj["osu"] = {}
								obj["twitch"] = {}

								obj["osu"]["name"] = self.osu_name
								obj["twitch"]["name"] = self.twitch_name
								obj["twitch"]["id"] = self.twitch_id

								file = json.loads(open("DATABASE/osu_twitch.json", "r").read())
								file["objects"].append(obj)
								with open("DATABASE/osu_twitch.json", "w") as save:
									self.BASE.queue.TO_OSU_T.put_nowait(self.BASE.Osu_IRC.send_message(self.osu_name, "Your account is now paired with Twitch acc: " + self.twitch_name))
									self.BASE.queue.TO_TWITCH_T.put_nowait(self.BASE.Twitch_IRC_connection.send_message(self.twitch_name, "Your account is now paired with Osu! acc: " + self.osu_name))
									json.dump(file, save)
									self.BASE.queue.twitch_osu_verify.remove(self)
