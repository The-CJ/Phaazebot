#BASE.moduls.Twitch

import time, asyncio, json, requests, random, os, discord, socket

vip_list = ["the__cj", "phaazebot"]
stream_nope = []

class _stream_(object):
	def __init__(self, code, art):
		if art == "file":
			self._id = str(code["ID"])
			self.live = code["live"]
			self.game = code["game"]
		if art == "weeb":
			self._id = str(code["channel"]["_id"])
			self.live = True
			self.game = code["game"]
		if art == "not_live":
			self._id = str(code["_id"])
			self.live = False
			self.game = ""

class u_streams(object):
	def __init__(self, new, old):
		self.old = old
		self.new = new

#BASE.twitch_alert_obj
class alerts(object):
	def __init__(self, BASE):
		self.running = True

		#add to BASE
		self.BASE = BASE
		BASE.twitch_alert_obj = self

		self.root = "https://api.twitch.tv/kraken/"
		self.stream_file_path = "UTILS/twitch_streams/"

		self.key = self.BASE.access.Twitch_API_Token

		self.header = {"Client-ID": self.key, "Accept": "application/vnd.twitchtv.v5+json"}

	def stop(self):
		self.running = False

	async def custom_call(self, _url):
		try:
			resp = requests.get(_url, headers = self.header)
			return resp.json()
		except:
			return {'status': 500}

	#loop func
	async def track(self):
		while self.running:

			if self.BASE.vars.discord_is_NOT_ready or self.BASE.vars.block_TW_alerts: continue

			old = open(self.stream_file_path + "_track.json", "r").read()
			old = json.loads(old)

			#old list
			list_with_old_stream_stats = [_stream_(s, "file") for s in old["streams"]]
			all_ids = [i["ID"] for i in old["streams"]]

			#get new stream info
			try:
				new = requests.get(self.root + "streams?channel={}".format(",".join(o["ID"] for o in old["streams"])), headers=self.header)
				new = new.json()
				if new.get("status", 200) >= 400:
					t = 0/0
			except:
				self.BASE.moduls.Console.RED("ERROR", "No Twitch API response")
				await asyncio.sleep(30)
				continue

			if self.BASE.vars.block_TW_alerts: continue

			#new list
			try:
				list_with_new_stream_stats = [_stream_(s, "weeb") for s in new["streams"]]
			except:
				with open("ERROR_REPORT.txt", "w") as err:
					json.dump(new, err)
					continue

			live_ids = [str(i["channel"]["_id"]) for i in new["streams"]]

			rest_list = list(set(all_ids) - set(live_ids))

			#add offline streams
			for _id_ in rest_list:
				i = {}
				i["_id"] = _id_
				list_with_new_stream_stats.append(_stream_(i, "not_live"))

			#update local data
			updated_file = {}
			updated_file["streams"] = []
			for _S_ in list_with_new_stream_stats:
				_ts_ = {}
				_ts_["ID"] = _S_._id
				_ts_["game"] = _S_.game
				_ts_["live"] = _S_.live

				updated_file["streams"].append(_ts_)
			with open("UTILS/twitch_streams/_track.json", "w") as save:
				json.dump(updated_file, save)

			#get difftents
			change = await self.BASE.moduls.Utils.list_XOR_async(list_with_old_stream_stats, list_with_new_stream_stats)

			#get object with 2 states (.old .new)
			change = await get__changes_from_old(list_with_old_stream_stats ,change)

			#get all infos from Twitch
			final_formated_list = []
			for c in change:
				infos = await get_back_twitch_infos(c.new._id, new)
				c.infos = infos
				final_formated_list.append(c)

			for C in final_formated_list:
				await self.BASE.twitch_alert_obj.check_if_live__format_and_send(C)

			if self.running: await asyncio.sleep(4)
			if self.running: await asyncio.sleep(4)
			if self.running: await asyncio.sleep(4)
			if self.running: await asyncio.sleep(4)
			if self.running: await asyncio.sleep(4)

	async def check_if_live__format_and_send(self, stream):
		#is live ?
		if not stream.new.live: return
		#is vodcast
		if not stream.infos.get("stream_type", "live") == "live":
			return

		#what kind of alert ?
		if stream.old.live == False and stream.new.live == True:
			_type_ = "live"

		elif stream.old.game != stream.new.game:
			_type_ = "game"

		file = open(self.stream_file_path + "{0}.json".format(stream.new._id), "r").read()
		file = json.loads(file)

		all_channels_phaaze_can_see = [o.id for o in self.BASE.phaaze.get_all_channels()]

		#for discord channels
		for channel in file["d_channel"]:
			if channel not in all_channels_phaaze_can_see: continue
			try:
				custom = open("UTILS/twitch_streams/custom_format/{0}.json".format(channel), "r").read()
				custom = json.loads(custom)

				template = custom["template"]
				c_text = custom["message"]
				no_game = custom["game"]

				if c_text != None:
					c_text = c_text.replace("[name]", stream.infos["channel"].get("display_name", "N/A"))
					c_text = c_text.replace("[game]", stream.infos["channel"].get("game", "N/A") if stream.infos.get("game", "N/A") != "" else "N/A")
					c_text = c_text.replace("[status]", stream.infos["channel"].get("status", "N/A"))
					c_text = c_text.replace("[everyone]", "@everyone")
					c_text = c_text.replace("[link]", stream.infos["channel"].get("url", "N/A"))

			except:
				template = 1
				c_text = "Now Live on Twitch:"
				no_game = False

			#don't want game updates
			if _type_ == "game" and no_game: continue

			#get embed
			temp = await self.BASE.twitch_alert_obj.get_stream_emb_temp(stream, template, _type_)

			self.BASE.queue.TO_DISCORD_T.put_nowait(self.BASE.phaaze.send_message(discord.Object(id=channel), content=c_text if _type_ == "live" else None, embed=temp))

	async def get_stream_emb_temp(self, stream, template, _type_):
		if _type_ == "live":

			if stream.infos["channel"]["display_name"].lower() in stream_nope:
				emb = discord.Embed(
						title="N/A",
						color=0x6441a5,
						description=":game_die: Playing: **{0}**".format("N/A"),
						url="https://www.twitch.tv"

						)
				emb.set_image(url="http://www-cdn.jtvnw.net/images/xarth/404_user_600x600.png")


				emb.set_author(	icon_url="http://www-cdn.jtvnw.net/images/xarth/404_user_600x600.png",
								url="https://www.twitch.tv",
								name="null")

				emb.set_footer(icon_url="http://i.imgur.com/N40pe8g.png", text="Provided by Twitch.tv")

				return emb

			if template == 0:
				template = 1

			elif template == 1: #normal
				emb = discord.Embed(
						title=stream.infos["channel"]["status"],
						color=0x6441a5,
						description=":game_die: Playing: **{0}**".format(stream.infos["game"] if stream.infos["game"] != "" else "N/A"),
						url=stream.infos["channel"]["url"]

						)
				emb.set_image(url=stream.infos["channel"]["logo"] if stream.infos["channel"]["logo"] != None else "http://www-cdn.jtvnw.net/images/xarth/404_user_600x600.png")


				emb.set_author(	icon_url=stream.infos["channel"]["logo"] if stream.infos["channel"]["logo"] != None else "http://www-cdn.jtvnw.net/images/xarth/404_user_600x600.png",
								url=stream.infos["channel"]["url"],
								name=stream.infos["channel"]["display_name"])

				if stream.infos["channel"]["display_name"].lower() not in vip_list:
					emb.set_footer(icon_url="http://i.imgur.com/N40pe8g.png", text="Provided by Twitch.tv")
				else:
					emb.set_footer(icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/Gold_Star.svg/2000px-Gold_Star.svg.png", text= "VIP | Provided by Twitch.tv")

				return emb

			elif template == 2: #slim
				emb = discord.Embed(
						title=stream.infos["channel"]["status"],
						color=0x6441a5,
						url=stream.infos["channel"]["url"],
						description=":game_die: Playing: **{0}**".format(stream.infos["game"] if stream.infos["game"] != "" else "N/A"),
						)

				emb.set_author(	icon_url=stream.infos["channel"]["logo"] if stream.infos["channel"]["logo"] != None else "http://www-cdn.jtvnw.net/images/xarth/404_user_600x600.png",
								url=stream.infos["channel"]["url"],
								name=stream.infos["channel"]["display_name"])

				if stream.infos["channel"]["display_name"].lower() not in vip_list:
					emb.set_footer(icon_url="http://i.imgur.com/N40pe8g.png", text="Provided by Twitch.tv")
				else:
					emb.set_footer(icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/Gold_Star.svg/2000px-Gold_Star.svg.png", text= "VIP | Provided by Twitch.tv")

				return emb

			elif template == 3: #infos
				emb = discord.Embed(
						title=stream.infos["channel"]["status"],
						color=0x6441a5,
						url=stream.infos["channel"]["url"]
						)

				emb.add_field(name="Playing:",value=stream.infos["game"] if stream.infos["game"] != "" else "N/A", inline=False)
				emb.add_field(name="ID:",value=str(stream.infos["channel"]["_id"]), inline=True)
				emb.add_field(name="FPS:",value=str(round(stream.infos["average_fps"])), inline=True)
				emb.add_field(name="Language:",value=stream.infos["channel"]["language"], inline=True)
				emb.add_field(name="Partner?:",value="Yes" if stream.infos["channel"]["partner"] else "No", inline=True)
				emb.add_field(name="Followers:",value=stream.infos["channel"]["followers"], inline=True)
				emb.add_field(name="Views:",value=stream.infos["channel"]["views"], inline=True)

				emb.set_thumbnail(url=stream.infos["channel"]["logo"])
				emb.set_image(url=stream.infos["preview"]["large"])
				emb.set_author(	icon_url=stream.infos["channel"]["logo"] if stream.infos["channel"]["logo"] != None else "http://www-cdn.jtvnw.net/images/xarth/404_user_600x600.png",
								url=stream.infos["channel"]["url"],
								name=stream.infos["channel"]["display_name"])

				if stream.infos["channel"]["display_name"].lower() not in vip_list:
					emb.set_footer(icon_url="http://i.imgur.com/N40pe8g.png", text="Provided by Twitch.tv")
				else:
					emb.set_footer(icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/Gold_Star.svg/2000px-Gold_Star.svg.png", text= "VIP | Provided by Twitch.tv")

				return emb

			else:
				return None

		elif _type_ == "game":

			if stream.infos["channel"]["display_name"].lower() in stream_nope:
				emb = discord.Embed(
						title="N/A",
						color=0x6441a5,
						description="Now Playing: **{0}**".format("N/A"),
						url="https://www.twitch.tv"
						)
				emb.set_thumbnail(url="http://www-cdn.jtvnw.net/images/xarth/404_user_600x600.png")
				emb.set_author(	icon_url="http://www-cdn.jtvnw.net/images/xarth/404_user_600x600.png",name="N/A")
				return emb

			emb = discord.Embed(
					title=stream.infos["channel"]["status"],
					color=0x6441a5,
					description="Now Playing: **{0}**".format(stream.infos["game"] if stream.infos["game"] != "" else "N/A"),
					url=stream.infos["channel"]["url"]
								)
			emb.set_thumbnail(url=stream.infos["channel"]["logo"])
			emb.set_author(	icon_url=stream.infos["channel"]["logo"] if stream.infos["channel"]["logo"] != None else "http://www-cdn.jtvnw.net/images/xarth/404_user_600x600.png",
							name=stream.infos["channel"]["display_name"])

			return emb

	async def translate_v3_v5(self, user_name):
		try:
			x = "users?login={0}".format(user_name)
			resp = requests.get(self.root + x, headers = self.header)
			resp = resp.json()
			check = resp.get("status", 200)

			if check in [400, 404, 422, 500, 503]: return None
			if resp["_total"] != 1: return None

			return resp["users"][0].get("_id", None)

		except:
			BASE.moduls.Console.RED("ERROR", "Twitch: Translating v3 in v5 failed")
			return None

	#GETS

	async def get_user(self, term, search="id"): # id or name
		try:
			if search == "id":
				s = "users/"
				link = self.root + s + term
				res = requests.get(link, headers=self.header)
				res = json.loads(res.text)
				if res.get("status", 200) == 400 or res.get("status", 200) == 422: return None
				return res

			elif search == "name":
				s = "users?login="
				link = self.root + s + term
				res = requests.get(link, headers=self.header)
				res = json.loads(res.text)

				#No User
				if res["_total"] != 1: return None

				return res["users"][0]

		except:
			return None

	#CREATE

	async def add_stream_status(self, BASE, s_id, REL_=False):
		r = open(self.stream_file_path + "_track.json", "r").read()
		r = json.loads(r)
		_a = [s["ID"] for s in r["streams"]]
		if s_id not in _a or REL_:
			_s_ = {}
			_s_["game"] = ""
			_s_["live"] = False
			_s_["ID"] = s_id

			r["streams"].append(_s_)

			with open(self.stream_file_path + "_track.json", "w") as save:
				json.dump(r, save)

				stea_f = {}
				stea_f["d_channel"] = []
				stea_f["t_channel"] = []

				stea_f["other_option_1"] = []
				stea_f["other_option_2"] = []
				stea_f["other_option_3"] = []

				with open(self.stream_file_path + "{0}.json".format(s_id), "w") as save_:
					json.dump(stea_f, save_)

		return

	async def add__rem_discord_channel(self, BASE, t_id, c_id):
		file = open(self.stream_file_path + "{0}.json".format(t_id), "r")
		file = json.loads(file.read())
		if c_id not in file["d_channel"]:
			file["d_channel"].append(c_id)
			x = "add"
		else:
			file["d_channel"].remove(c_id)
			x = "rem"

		with open(self.stream_file_path + "{0}.json".format(t_id), "w") as save:
			json.dump(file, save)
			return x

async def twitch_alerts_base(BASE, message):
	av_o = ["track", "custom", "get", "reset"]
	m = message.content.split(" ")

	if len(m) == 1:
			return await BASE.phaaze.send_message(message.channel, ":warning: You need to add a option, available are: {0}".format(" ".join("`" + g + "`" for g in av_o)))

	if m[1].lower() == "track":
		if len(m) == 2:
			return await BASE.phaaze.send_message(message.channel, ":warning: You need to add a Twitch channel name to enable/disable alerts")

		#get channel + check if a real channel
		i = await BASE.twitch_alert_obj.get_user(m[2], search="name")
		if i == None:
			return await BASE.phaaze.send_message(message.channel, ":warning: There is not channel called: `{}`\nOr Twitch API is down. Make sure you don't make a typo and try again.".format(m[2]))

		#block edits from TW_A
		BASE.vars.block_TW_alerts = True

		await BASE.twitch_alert_obj.add_stream_status(BASE, i["_id"])
		_new_ = await BASE.twitch_alert_obj.add__rem_discord_channel(BASE, i["_id"], message.channel.id)

		BASE.vars.block_TW_alerts = False

		if _new_ == "add":
			return await BASE.phaaze.send_message(message.channel, ":white_check_mark: **{0}** is now tracked in {1} :large_blue_circle:".format(i["display_name"], message.channel.mention))
		else:
			return await BASE.phaaze.send_message(message.channel, ":white_check_mark: **{0}** will no longer be tracked in {1} :red_circle:".format(i["display_name"], message.channel.mention))

	elif m[1].lower() == "custom":
		if len(m) == 2:
			await BASE.phaaze.send_message(message.channel, ":warning: missing option: `message`, `game` or `template`")
		elif m[2].lower() == "message":
			await change_custom_settings(BASE, message, "message")
		elif m[2].lower() == "game":
			await change_custom_settings(BASE, message, "game")
		elif m[2].lower() == "template":
			await change_custom_settings(BASE, message, "template")
		else:
			await BASE.phaaze.send_message(message.channel, ":warning: `{0}` is not a option, try: `message`, `game` or `template`".format(m[2].lower()))

	elif m[1].lower() == "get":
		found = []
		for file in os.listdir("UTILS/twitch_streams"):
			if file.endswith(".json") and not file.startswith("_"):
				with open("UTILS/twitch_streams/"+file, "r") as stream_file:
					stream_file = json.loads(stream_file.read())
					if message.channel.id in stream_file["d_channel"]:
						found.append(file.replace(".json", ""))

		response = await twitch_API_call(BASE, "https://api.twitch.tv/kraken/users?id=" + ",".join(_id for _id in found))

		if response.get("stats", 200) == 400:
			return await BASE.phaaze.send_message(message.channel, ":information_source: No active Twitch Alerts in {0}".format(message.channel.mention))

		if response.get("_total", 0) == 0:
			return await BASE.phaaze.send_message(message.channel, ":information_source: No active Twitch Alerts in {0}".format(message.channel.mention))

		found_names = [stream["display_name"] for stream in response["users"]]

		e = ", ".join(name for name in found_names)
		return await BASE.phaaze.send_message(message.channel, ":information_source: Twitch Alerts in {0} for Twitch Channels: {1}".format(message.channel.mention, e))

	elif m[1].lower() == "reset":
		pass

	else:
		return await BASE.phaaze.send_message(message.channel, ":warning: `{1}` is not a option, available are: {0}".format(" ".join("`" + g + "`" for g in av_o), m[1]))

async def get__changes_from_old(old, changes):
	CHA = []
	def get_opposite(_id, o):
		for s in o:
			if _id == s._id: return s

	c = [vars(o) for o in old]

	old_s = []
	new_s = []

	#is old or new
	for s in changes:
		if vars(s) in c:
			old_s.append(s)
		else:
			new_s.append(s)

	#for each new, get opposite
	for n in new_s:
		n_ = get_opposite(n._id, old_s)

		#make 2 state object
		CHA.append(u_streams(n, n_))

	return CHA

async def get_back_twitch_infos(_id ,new):
	for stream in new["streams"]:
		if stream["channel"]["_id"] == int(_id): return stream

async def change_custom_settings(BASE, message, _type_):
	m = message.content.split(" ")
	try:
		a = open("UTILS/twitch_streams/custom_format/{0}.json".format(message.channel.id), "r").read()
		a = json.loads(a)
	except:
		a = {}
		a["message"] = "Now Live on Twitch:"
		a["game"] = False
		a["template"] = 1

	if _type_ == "template":
		if len(m) == 3:
			ccv = discord.Embed()
			ccv.set_image(url="https://puu.sh/ueUPa/61ac7e684a.png")
			return await BASE.phaaze.send_message(message.channel, content=":information_source: {0} is currently template #**{1}**\nType `{2}{2}{2}twitch change template [X]` to change".format("Stream template", str(a["template"]), BASE.vars.PT), embed=ccv)
		nb = int(m[3])
		if not 1 <= nb <= 3:
			return await BASE.phaaze.send_message(message.channel, content=":warning: [X] must be in range 1 - 3, try again")

		a["template"] = nb

		with open("UTILS/twitch_streams/custom_format/{0}.json".format(message.channel.id), "w") as save:
			json.dump(a, save)
			return await BASE.phaaze.send_message(message.channel, content=":white_check_mark: Stream template in {1} set to number: {0}".format(str(nb), message.channel.mention))

	elif _type_ == "game":

		a["game"] = False if a["game"] == True else True

		with open("UTILS/twitch_streams/custom_format/{0}.json".format(message.channel.id), "w") as save:
			json.dump(a, save)
			return await BASE.phaaze.send_message(message.channel, content=":white_check_mark: Game change alerts in {1} has been: **{0}**".format("disabled" if a["game"] else "enabled", message.channel.mention))

	elif _type_ == "message":
		if len(m) == 3:
			return await BASE.phaaze.send_message(message.channel, 	":information_source: The stream message is currently:\n"\
																	"```\n{1}```it will appear above every Twitch `live` event card.\n\n"\
																	"Type: `{0}{0}{0}twitch custom message [Your Message]` to change\n\n"\
																	"This message can have tokens, that will be replaced:\n"\
																	"`[name]` - Streamer Name\n"\
																	"`[game]` - Current Game\n"\
																	"`[status]` - Current Stream Title/Status\n"\
																	"`[everyone]` - Will be replaced with a `@everyone`\n"\
																	"`[link]` - Link to stream (not really necessary, link is always included in a stream card)".format(BASE.vars.PT, a["message"]))

		if m[3] == "":
			return await BASE.phaaze.send_message(message.channel, 	":warning: Your message can't be/start with \"\" (nothing) if you wanna clear the message completly use: `...custom message clear`")

		if m[3].lower() == "clear":
			a["message"] = None
			with open("UTILS/twitch_streams/custom_format/{0}.json".format(message.channel.id), "w") as save:
				json.dump(a, save)
				return await BASE.phaaze.send_message(message.channel, content=":white_check_mark: Twitch Live message for {0} has been removed".format(message.channel.mention))

		me = " ".join(d for d in m[3:])

		a["message"] = me

		with open("UTILS/twitch_streams/custom_format/{0}.json".format(message.channel.id), "w") as save:
			json.dump(a, save)
			me = me.replace("[name]", "Phaazebot")
			me = me.replace("[game]", "Creative")
			me = me.replace("[status]", "[Ger/Eng] Trying a new alert :3")
			me = me.replace("[everyone]", "[at]everyone")
			me = me.replace("[link]", "https://www.twitch.tv/phaazebot")

			return await BASE.phaaze.send_message(message.channel, content=":white_check_mark: Twitch Live message for {1} has been updated: e.g. with Phaazebot:\n\n{0}".format(me, message.channel.mention))


	return

async def twitch_API_call(BASE, url):
	key = BASE.access.Twitch_API_Token
	header = {"Client-ID": key, "Accept": "application/vnd.twitchtv.v5+json"}
	try:
		resp = requests.get(url, headers = header)
		return resp.json()
	except:
		return {'status': 500}
