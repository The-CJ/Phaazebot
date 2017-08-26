#BASE.moduls.osu

import asyncio, requests, re, discord

##Mode
#"0" | "osu"
#"1" | "taiko"
#"2" | "ctb"
#"3" | "mania"

MAIN = "https://osu.ppy.sh/api/"
USER = "get_user"
MAP = "get_beatmaps"

class default_format(object):
	osu = "[[osu_link] [titel] [[version]]] ★ [stars] | Lenght: [lenght]min | BPM: [bpm] >> [requester]"
	osu_link_format = "http://osu.ppy.sh/b/[id]"
	twitch = "[titel] [[version]] by [creator] | ★ [stars] | Lenght: [lenght]min | BPM: [bpm]"

async def get_user(BASE, user=None, mode="0"):
	if user == None: return None

	result = requests.get(MAIN + USER + "?k="+BASE.access.Osu_API_Token + "&m={0}&u={1}".format(mode, user))
	result = result.json()

	#not found
	if result == []: return None
	else: result = result[0]

	class user_info(object):
		def __init__(self, result):

			if mode == "0": mode_name = "osu!"
			if mode == "1": mode_name = "osu!taiko"
			if mode == "2": mode_name = "osu!ctb"
			if mode == "3": mode_name = "osu!mania"

			self.json = result
			self.mode = mode
			self.mode_name = mode_name
			self.name = result["username"]
			self.user_id = result["user_id"]
			self.playcount = result["playcount"]

			self.pp = result["pp_raw"]
			self.level = result["level"]
			self.acc = result["accuracy"]

			self.rank = result["pp_rank"]
			self.country_rank =result["pp_country_rank"]
			self.country = result["country"].lower()

			self.total_score = result["total_score"]
			self.ranked_score = result["ranked_score"]

			self.count_50 = result["count50"]
			self.count_100 = result["count100"]
			self.count_300 = result["count300"]
			self.count_A = result["count_rank_a"]
			self.count_S = result["count_rank_s"]
			self.count_SS = result["count_rank_ss"]

	return user_info(result)

async def get_all_maps(BASE, ID=None, mode="b"):
	KEY = "?k={0}".format(BASE.access.Osu_API_Token)

	if ID == None: return None

	#request stuff
	r = requests.get(MAIN + MAP + "?k="+BASE.access.Osu_API_Token + "&{0}={1}".format(mode, ID))
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
		return await BASE.phaaze.send_message(message.channel, ":warning: Missing Maplink (and options)\n\nOptions:\n`acc=[X]` - e.g. `acc=98,4` \n`combo=[X]` - e.g. `combo=1455` (0 == Full Combo)\n`miss=[X]` - e.g. `miss=4`\n`mods=[X]` - e.g. `mods=HDHR`\n\n**options seperated with Spaces**")

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
			return await BASE.phaaze.send_message(message.channel, ":warning: PP Calc only works for single maps, not mapsets")
		if map_id_number == None:
			return await BASE.phaaze.send_message(message.channel, ":warning: Invalid Maplink. Only Map link or ID are vaild.")

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
						return await BASE.phaaze.send_message(message.channel, ":warning: `acc` value has to be 0 < [X] <= 100.")
					acc_ = v
				except: return await BASE.phaaze.send_message(message.channel, ":warning: `acc` value can only be a *int* or *float*.")

			elif option.lower().startswith("combo="):
				try:
					v = int(option.split("=")[1])
					combo_ = v
				except: return await BASE.phaaze.send_message(message.channel, ":warning: `combo` value can only be a *int* from 0-[max_combo].")

			elif option.lower().startswith("miss="):
				try:
					v = int(option.split("=")[1])
					miss_ = v
				except: return await BASE.phaaze.send_message(message.channel, ":warning: `miss` value can only be a *int* from 0-[max_hit_obj].")

			elif option.lower().startswith("mods="):
				try:
					v = option.split("=")[1].upper()
					mods_ = v
				except: return await BASE.phaaze.send_message(message.channel, ":warning: Invaild syntax for `mods`.")

			else:
				return await BASE.phaaze.send_message(message.channel, ":warning: Invalid Option, `{0}` could not be processed, available are `mods`, `acc`, `combo` and `miss`".format(option))

	result = await BASE.moduls.osu_utils.get_pp(map_id_number, acc=acc_, misses=miss_, combo=combo_, mod_s=mods_)

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

	return await BASE.phaaze.send_message(message.channel, embed=osu_aw)

#-------

async def twitch_osu(BASE, message):
	def get_link_out_of_content(content):
		m = content.lower().split()
		for word in m:
			if "osu.ppy.sh/b/" in word:
				return word.split("/b/")[1], "b"
			if "osu.ppy.sh/s/" in word:
				return word.split("/s/")[1], "s"
		return "835314&m=0", "b"

	search_id, mode = get_link_out_of_content(message.content)

	osu_user = await BASE.moduls._Twitch_.Utils.get_opposite_osu_twitch(BASE, message.room_id, platform="twitch")
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
