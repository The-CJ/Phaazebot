#BASE.moduls._Osu_.Utils

import asyncio, random, json
already_in_pairing_proccess = []

async def verify(BASE, message):
	m = message.content.split(" ")

	if len(m) == 1:
		confirm = await BASE.moduls._Twitch_.Utils.get_opposite_osu_twitch(BASE, message.name, platform="osu")
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
			self.BASE.moduls._Twitch_.CMD.Mods.already_in_pairing_proccess.remove(self.twitch_id)

		if self.osu_name != None:
			self.BASE.moduls._Osu_.Utils.already_in_pairing_proccess.remove(self.osu_name)

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
