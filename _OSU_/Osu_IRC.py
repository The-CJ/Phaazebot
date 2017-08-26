#BASE.moduls._Osu_.IRC

import time, discord, requests, socket, asyncio, json

class _IRC_():
	def __init__(self, BASE):
		self.BASE = BASE
		BASE.Osu_IRC = self

		self.server = "irc.ppy.sh"
		self.port = 6667
		self.last_ping = time.time()

		self.oauth = self.BASE.access.Osu_IRC_Token
		self.nickname = "Phaazebot"

		self.hold_connetion_open = True
		self.connection = None

	#utils
	async def send_pong(self):
		self.connection.send(bytes("PONG :cho.ppy.sh\r\n", 'UTF-8'))

	async def send_nick(self):
		self.connection.send(bytes("NICK {0}\r\n".format(self.nickname), 'UTF-8'))

	async def send_pass(self):
		self.connection.send(bytes("PASS {0}\r\n".format(self.oauth), 'UTF-8'))

	async def save_print_raw_data(self, data):
		b = ""
		for char in data:
			if ord(char) < 256:
				b = b + char

		print(b)

	#comms
	async def send_message(self, channel, message):
		if self.hold_connetion_open: self.connection.send(bytes("PRIVMSG {0} :{1}\r\n".format(channel.lower(), message), 'UTF-8'))

	async def join_channel(self, channel):
		if self.hold_connetion_open: self.connection.send(bytes("JOIN #{0}\r\n".format(channel.lower()), 'UTF-8'))

	async def part_channel(self, channel):
		if self.hold_connetion_open: self.connection.send(bytes("PART #{0}\r\n".format(channel.lower()), 'UTF-8'))

	#main connection
	async def run(self):
		while self.BASE.active.osu_irc:
			self.last_ping = time.time()

			#init connection
			if self.hold_connetion_open:
				#connect to server
				setattr(self, "connection", socket.socket())
				try:
					self.connection.connect((self.server, self.port))
				except:
					self.BASE.moduls.Console.RED("ERROR", "Unable to connect to the Osu IRC")
					self.connection.close()
					self.last_ping = time.time()
					await asyncio.sleep(10)
					continue

				self.connection.settimeout(0.005)

				#login
				await self.send_pass()
				await self.send_nick()

				self.BASE.vars.osu_IRC_is_NOT_ready = False

			while self.hold_connetion_open == True and self.BASE.active.osu_irc:
				data_cluster = ""

				disconnected = int(time.time()) - int(self.last_ping)
				if int(disconnected) > 300:
					#Osu issn't pinging us, most likly means connection timeout --> Reconnect
					self.BASE.moduls.Console.RED("ERROR", "No Osu! IRC Server response")
					self.connection.close()
					break

				try:
					data_cluster = data_cluster + self.connection.recv(4096).decode('UTF-8')
					data_cluster_parts = data_cluster.splitlines()

					if len(data_cluster_parts) == 0:
						#Osu send nothing, most likly means connection timeout --> Reconnect
						break

					#Osu can give more than one segment in one datacluster
					for data in data_cluster_parts:
						#just to be sure
						if data == "" or data == " " or data == None: continue

						#save, no Unicode debug print of all data
						if not "cho@ppy.sh QUIT" in data:
							pass
							#await self.save_print_raw_data(data)

						#we are connected
						if ":cho.ppy.sh 001" in data:
							self.BASE.moduls.Console.GREEN("SUCCESS", "Osu! IRC Connected")

						#response to PING
						if data.startswith("PING"):
							self.last_ping = time.time()
							await self.send_pong()

						#on_message
						if "cho@ppy.sh PRIVMSG" in data:
							message = Get_classes_from_data.message(data)
							asyncio.ensure_future(self.BASE.moduls._Osu_.Base.on_message(self.BASE, message))

				except socket.timeout:
					await asyncio.sleep(0.025)

			else:
				#connection is ordert to close and wait for restart
				self.connection.close()
				self.BASE.moduls.Console.CYAN("REMOTE", "Osu IRC connection has been disabled")
				while not self.hold_connetion_open:
					#holding connection "trapped" in a endless loop
					await asyncio.sleep(1)
				else:
					#connection is ordert to reconnect
					self.BASE.moduls.Console.CYAN("REMOTE", "Osu IRC connection has been enabled")
					continue

class Get_classes_from_data(object):
	"""Class contains all init-classes for Osu IRC data"""

	class message(object):
		def __init__(self, data):
			self.name = None
			self.content = None

			self.info(data)

		def info(self, data):
			try:
				self.name = data.split("!", 1)[0][1:]
				self.content = data.split(" :", 1)[1]
			except: pass
