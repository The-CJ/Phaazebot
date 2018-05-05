#BASE.modules.Twitch_IRC

import time, twitch, socket, asyncio, json, re

#BASE.twitch
class Init_twitch():
	def __init__(self, BASE, token=None, nickname=None):
		self.BASE = BASE

		self.running = False

		self.token = token
		self.nickname = nickname
		self.server = "irc.twitch.tv"
		self.port = 6667
		self.last_ping = time.time()

		self.connection = None
		self.channels = {}

		self.traffic = 0

	async def stop(self):
		self.running = False
		await asyncio.sleep(0.5)
		self.connection.close()

	#utils
	async def send_pong(self):
		self.connection.send(bytes("PONG :tmi.twitch.tv\r\n", 'UTF-8'))

	async def send_nick(self):
		self.connection.send(bytes("NICK {0}\r\n".format(self.nickname), 'UTF-8'))

	async def send_pass(self):
		self.connection.send(bytes("PASS {0}\r\n".format(self.token), 'UTF-8'))

	async def req_membership(self):
		self.connection.send(bytes("CAP REQ :twitch.tv/membership\r\n", 'UTF-8'))

	async def req_commands(self):
		self.connection.send(bytes("CAP REQ :twitch.tv/commands\r\n", 'UTF-8'))

	async def req_tags(self):
		self.connection.send(bytes("CAP REQ :twitch.tv/tags\r\n", 'UTF-8'))

	async def save_print_raw_data(self, data):
		b = ""
		for char in data:
			if ord(char) < 256:
				b = b + char

		print(b)

	#comms
	async def send_message(self, channel, message):
		if self.traffic <= 29:
			self.connection.send(bytes("PRIVMSG #{0} :{1}\r\n".format(channel.lower(), message), 'UTF-8'))
			self.traffic += 1
		else:
			self.BASE.queue.TO_TWITCH_T.put_nowait(self.send_message(channel, message))

	async def join_channel(self, channel):
		self.connection.send(bytes("JOIN #{0}\r\n".format(channel.lower()), 'UTF-8'))
		#if not channel.lower() in [c.name for c in self.channels]:
		#	self.channels.append(channel_class(self.BASE, channel))

	async def part_channel(self, channel):
		self.connection.send(bytes("PART #{0}\r\n".format(channel.lower()), 'UTF-8'))
		#if channel in [c.name for c in self.channels]:
		#	for c in self.channels:
		#		if c.name.lower() == channel.lower():
		#			self.channels.remove(c)

	async def join_all_channel(self):
		file = json.loads(open("_TWITCH_/_achtive_channels.json", "r").read())
		for channel in file.get("channels", []):
			await self.join_channel(channel)
			await asyncio.sleep(30/50)

		self.BASE.modules.Console.CYAN("INFO", "Joined: {} Twitch channels".format(str(len(file.get("channels", [])))))

	#main connection
	async def run(self):
		self.running = True
		self.last_ping = time.time()

		while self.running:

			#init connection
			self.connection = socket.socket()
			self.last_ping = time.time()

			try:
				self.connection.connect((self.server, self.port))
			except:
				self.BASE.modules.Console.RED("ERROR", "Unable to connect to the Twitch IRC")
				self.connection.close()
				self.last_ping = time.time()
				await asyncio.sleep(10)
				continue

			self.connection.settimeout(0.005)

			#login
			await self.send_pass()
			await self.send_nick()

			#get infos
			await self.req_membership()
			await self.req_commands()
			await self.req_tags()

			#join main channel
			await self.join_channel(self.nickname)
			#asyncio.ensure_future( self.join_all_channel() ) #FIXME:

			self.BASE.is_ready.twitch = True

			#listen to twitch
			while self.running:
				raw_data_bytes = ""

				disconnected = int(time.time()) - int(self.last_ping)
				if int(disconnected) > 800:
					#Twitch issn't pinging us, most likly means connection timeout --> Reconnect
					self.BASE.modules.Console.RED("ERROR", "No Twitch IRC Server response")
					self.connection.close()
					break

				try:
					raw_data_bytes = raw_data_bytes + self.connection.recv(4096).decode('UTF-8')
					raw_data = raw_data_bytes.splitlines()

					if len(raw_data) == 0:
						#Twitch send nothing, most likly means connection timeout --> Reconnect
						break

					for data in raw_data:
						#Twitch can give more than one segment in a datacluster

						#save, no Unicode debug print of all data
						#await self.save_print_raw_data(data) # DEBUG:

						#just to be sure
						if data in ["", " ", None]: continue

						#response to PING
						elif re.match(r'^PING', data) != None:
							self.last_ping = time.time()
							await self.send_pong()

						#we are connected
						elif re.match(r"^:tmi\.twitch\.tv 001.*", data) != None:
							self.BASE.modules.Console.GREEN("SUCCESS", "Twitch IRC Connected")

						#on_message
						elif re.match(r'^@.+\.tmi\.twitch\.tv PRIVMSG #.+', data) != None:
							message = OBJECT_GENERATOR.Message(data)
							asyncio.ensure_future( self.on_message(message) )

						#on_member_join
						elif re.match(r"^:tmi.+\.twitch\.tv JOIN #.+", data) != None:
							name = data.split("!")[1]
							name = name.split("@")[0]

							channel = data.split("#")[1]

							asyncio.ensure_future( self.BASE.modules._Twitch_.Base.on_member_join(self.BASE, channel, name) )

						#on_member_leave
						if "tmi.twitch.tv PART #" in data and data.startswith(":"):
							name = data.split("!")[1]
							name = name.split("@")[0]

							channel = data.split("#")[1]

							asyncio.ensure_future( self.BASE.modules._Twitch_.Base.on_member_leave(self.BASE, channel, name) )

						#on other event
						if ":tmi.twitch.tv USERNOTICE #" in data and data.startswith("@"):
							event = re.search(r"msg-id=(.*?);", data)
							if event != None:
								event = event.group(1)

							#Sub event
							if event in ["resub","sub"]:

								try:
									sub_message = Get_classes_from_data.Twitch_sub(data)
									asyncio.ensure_future( self.BASE.modules._Twitch_.Base.on_sub(self.BASE, sub_message) )
								except:
									self.BASE.modules.Console.RED("ERROR", "Failed to process Twitch Sub")
									continue

							#Raid event
							if event in ["raid"]:
								return #TODO: Make something with this
								try:
									raid__message = Get_classes_from_data.Twitch_sub(data)
									asyncio.ensure_future( self.BASE.modules._Twitch_.Base.on_raid(self.BASE, raid__message) )
								except:
									self.BASE.modules.Console.RED("ERROR", "Failed to process Twitch Sub")
									continue


				except socket.timeout:
					await asyncio.sleep(0.025)

			self.BASE.is_ready.twitch = False

	#events
	async def on_message(self, message):
		pass

class OBJECT_GENERATOR(object):
	"""Class contains all init-classes for Twitch IRC data"""

	class Message(object):
		def __init__(self, data):
			self.raw = data

			self.badges = None
			self.color = None
			self.name= None
			self.display_name = None
			self.emotes = []
			self.message_id = None
			self.mod = None
			self.room_id = None
			self.sub = None
			self.turbo = None
			self.user_id = None
			self.type = None
			self.save_name = None

			self.channel = None
			self.content = None

			self.process()

		def get_badges(self, arg):
			"""@badges=moderator/1,premium/1"""

			x = arg.split("=")[1]

			if len(x) <= 1:
				return

			self.badges = x.split(",")

		def get_color(self, arg):
			"""color=#696969"""

			x = arg.split("=")[1]

			if len(x) <= 1:
				return

			self.color = x

		def get_display_name(self, arg):
			"""display-name=The__CJ"""

			x = arg.split("=")[1]

			if len(x) <= 1:
				return

			self.display_name = x

		def get_emotes(self, arg):
			"""emotes=1902:6-10/25:0-4,12-16"""
			#[{"index": 1902, "ammount": 1}, {"index": 25, "ammount": 2}]

			x = arg.split("=")[1]

			if len(x) <= 1:
				return

			emote_list = []
			different_emotes = x.split("/")

			for emote in different_emotes:
				index, rest = emote.split(":")

				d = dict()
				d["index"] = int(index)
				d["ammount"] = len(rest.split(","))

				emote_list.append(d)

			self.emotes = emote_list

		def get_message_id(self, arg):
			"""id=067a9351-a907-4196-9a30-30f57cf8d0d0"""

			x = arg.split("=")[1]

			if len(x) <= 1:
				return

			self.message_id = x

		def get_mod(self, arg):
			"""mod=1"""

			x = arg.split("=")[1]

			if x == "1":
				self.mod = True

			else:
				self.mod = False

		def get_room_id(self, arg):
			"""room-id=94638902"""

			x = arg.split("=")[1]

			if len(x) <= 1:
				return

			self.room_id = x

		def get_sub(self, arg):
			"""subscriber=0"""

			x = arg.split("=")[1]

			if x == "1":
				self.sub = True
			else:
				self.sub = False

		def get_turbo(self, arg):
			"""turbo=0"""

			x = arg.split("=")[1]

			if x == "1":
				self.turbo = True
			else:
				self.turbo = False

		def get_user_id(self, arg):
			"""user-id=67664971"""

			x = arg.split("=")[1]

			if len(x) <= 1:
				return

			self.user_id = x

		def get_user_type(self, arg):
			"""user-type=mod"""

			x = arg.split("=")[1]

			if len(x) <= 1:
				return

			self.type = x

		def process(self):
			sdp_1, sdp_2 = self.raw.split(" :", 1)
			message_data = sdp_1.split(";")
			name__channel__content = sdp_2

			for argument in message_data:
				if argument.startswith("user-type"):
					self.get_user_type(argument)
				elif argument.startswith("user-id"):
					self.get_user_id(argument)
				elif argument.startswith("turbo"):
					self.get_turbo(argument)
				elif argument.startswith("subscriber"):
					self.get_sub(argument)
				elif argument.startswith("room-id"):
					self.get_room_id(argument)
				elif argument.startswith("mod"):
					self.get_mod(argument)
				elif argument.startswith("id"):
					self.get_message_id(argument)
				elif argument.startswith("emotes"):
					self.get_emotes(argument)
				elif argument.startswith("display-name"):
					self.get_display_name(argument)
				elif argument.startswith("color"):
					self.get_color(argument)
				elif argument.startswith("@badges"):
					self.get_badges(argument)
				else:
					pass

			self.more_process(name__channel__content)

		def more_process(self, data):
			""""the__cj!the__cj@the__cj.tmi.twitch.tv PRIVMSG #phaazebot :Kappa Keepo hi"""

			n, c = data.split(".tmi.twitch.tv PRIVMSG #", 1)

			self.name = n.split("@")[1]
			self.channel, self.content = c.split(" :", 1)

			self.save_name = self.display_name if self.display_name != None else self.name

	class Twitch_sub(object):
		eg_mg = "@badges=staff/1,broadcaster/1,turbo/1;"\
				"color=#008000;"\
				"display-name=ronni;"\
				"emotes=;"\
				"mod=0;"\
				"msg-id=resub;"\
				"msg-param-months=6;"\
				"msg-param-sub-plan=Prime;"\
				"msg-param-sub-plan-name=Prime;"\
				"room-id=1337;"\
				"subscriber=1;"\
				"system-msg=ronni\shas\ssubscribed\sfor\s6\smonths!;"\
				"login=ronni;"\
				"turbo=1;"\
				"user-id=1337;"\
				"user-type=staff "\
				":tmi.twitch.tv USERNOTICE #dallas :Great stream -- keep it up!"
		def __init__(self, data):
			self.raw = data

			self.display_name = None
			self.name = None
			self.months = None
			self.room_id = None
			self.user_id = None
			self.channel = None

			self.process()

		def process(self):
			search_object = re.search(r"USERNOTICE #(\w+) :", self.raw)
			if search_object != None:
				self.channel = search_object.group(1)

			#display-name=RoNnI;
			search_object = re.search(r"display-name=(.+?);", self.raw)
			if search_object != None:
				self.display_name = search_object.group(1)

			#login=ronni;
			search_object = re.search(r"login=(.+?);", self.raw)
			if search_object != None:
				self.login = search_object.group(1)

			#msg-param-months=6;
			search_object = re.search(r"msg-param-months=(.+?);", self.raw)
			if search_object != None:
				self.months = search_object.group(1)

			#room-id=1337;
			search_object = re.search(r"room-id=(.+?);", self.raw)
			if search_object != None:
				self.room_id = search_object.group(1)

			#user-id=69;
			search_object = re.search(r"user-id=(.+?);", self.raw)
			if search_object != None:
				self.user_id = search_object.group(1)

class channel_class(object):
	def __init__(self, BASE, name):
		self.name = name.lower()
		self.room_id = str(get_id_from_room_name(BASE, self.name))
		self.user = []
		self.live = False
