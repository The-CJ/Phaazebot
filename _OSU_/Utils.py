#BASE.modules._Osu_.Utils

import asyncio, random, json,requests, discord, re
from UTILS import oppai as oppai

MAIN = "https://osu.ppy.sh/api/"
USER = "get_user"
MAP = "get_beatmaps"

async def download_map(ID):
	link = "https://osu.ppy.sh/osu/" + ID
	h = requests.get(link)
	return h.text

async def get_pp(file, c100=0, c50=0, misses=0, sv=1, acc=100.0, combo=0, mod_s=""):

	e = oppai.calc(file, c100=c100, c50=c50, misses=misses, sv=sv, acc=acc, combo=combo, mod_s=mod_s)

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

async def get_maps(BASE, ID=None, mode="b"):
	KEY = "?k={0}".format(BASE.access.Osu_API_Token)

	if ID == None: return None

	#request maps
	r_str = MAIN + MAP + KEY + "&{0}={1}".format(mode, ID)
	r = requests.get(r_str)
	r = r.json()

	#No result
	if r == []: return None

	def sort_in_mapsets(maps):
		result_dict = dict()

		for osu_map in maps:
			map_set = result_dict.get(osu_map.set_id, [])
			map_set.append(osu_map)
			result_dict[str(osu_map.set_id)] = map_set

		return result_dict

	class Results(object):
		def __init__(self, response, mode):

			if mode == "b": mode_name = "Single_map"
			if mode == "s": mode_name = "Beatmap_set"
			if mode == "u": mode_name = "User_maps"

			self.result = response
			self.mode = mode
			self.mode_name = mode_name

			#convert all things into objects
			self.all_maps = [Map_Object(map_dict) for map_dict in response]
			self.map_sets = sort_in_mapsets(self.all_maps)

	return Results(r, mode)

async def pp_calc_for_maps(BASE, message): # TODO: Remove
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

class Map_Object(object):
	def __init__(self, info):
		self.info = info

		#meta
		self.approved = None
		self.approved_symbol = None
		self.approved_name = None
		self.set_id = None
		self.map_id = None
		self.favourite_count = None
		self.tags = None

		#infos
		self.version = None
		self.artist = None
		self.title = None
		self.creator = None
		self.source = None

		#diff
		self.diff = None
		self.cs = None
		self.od = None
		self.ar = None
		self.hp = None
		self.bpm = None

		#time
		self.lenght = None
		self.drain = None

		#stuff
		self.playcount = None
		self.passcount = None

		self.process()

		del self.info

	def process(self):
		#4 = loved, 3 = qualified, 2 = approved, 1 = ranked, 0 = pending, -1 = WIP, -2 = graveyard
		if self.info["approved"] == "-2":
			self.approved = "-2"
			self.approved_name = "Graveyard"
		elif self.info["approved"] == "-1":
			self.approved = "-1"
			self.approved_name = "WIP"
		elif self.info["approved"] == "0":
			self.approved = "0"
			self.approved_name = "Pending"
		elif self.info["approved"] == "1":
			self.approved = "1"
			self.approved_name = "Ranked"
		elif self.info["approved"] == "2":
			self.approved = "2"
			self.approved_name = "Approved"
		elif self.info["approved"] == "3":
			self.approved = "3"
			self.approved_name = "Qualified"
		elif self.info["approved"] == "4":
			self.approved = "4"
			self.approved_name = "Loved"
		else:
			self.approved = None
			self.approved_name = None
		self.approved_symbol = self.get_osu_status_symbol()

		#meta
		self.set_id = self.info["beatmapset_id"]
		self.map_id = self.info["beatmap_id"]
		self.favourite_count = self.info["favourite_count"]
		self.tags = self.info["tags"].split(" ")

		#infos
		self.version = self.info["version"]
		self.artist = self.info["artist"]
		self.title = self.info["title"]
		self.creator = self.info["creator"]
		self.source = self.info["source"]

		#diff
		self.diff = float(self.info["difficultyrating"])
		self.cs = float(self.info["diff_size"])
		self.od = float(self.info["diff_overall"])
		self.ar = float(self.info["diff_approach"])
		self.hp = float(self.info["diff_drain"])
		self.bpm = float(self.info["bpm"])

		#time
		F_minutes, F_seconds = divmod(int(self.info["total_length"]), 60)
		D_minutes, D_seconds = divmod(int(self.info["hit_length"]), 60)
		self.lenght = str(F_minutes) + "," + str(F_seconds if F_seconds >= 10 else "0" + str(F_seconds))
		self.drain = str(D_minutes) + "," + str(D_seconds if D_seconds >= 10 else "0" + str(D_seconds))

		#stuff
		self.playcount = self.info["playcount"]
		self.passcount = self.info["passcount"]

	def get_osu_status_symbol(self):
		#4 = loved, 3 = qualified, 2 = approved, 1 = ranked, 0 = pending, -1 = WIP, -2 = graveyard
		if self.approved == "-2":
			return ":cross:"
		elif self.approved == "-1":
			return ":tools:"
		elif self.approved == "0":
			return ":clock1:"
		elif self.approved == "1":
			return ":large_blue_diamond:"
		elif self.approved == "2":
			return ":fire:"
		elif self.approved == "3":
			return ":sweat_drops:"
		elif self.approved == "4":
			return ":heart:"
		else: return ":question:"
