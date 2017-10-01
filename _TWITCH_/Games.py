#BASE.moduls._Twitch_.Games

import asyncio, random

"""Global game storage"""
active_battle_games = []
active_missions = []

"""Battle game"""
async def battle(BASE, message):
	file = await BASE.moduls._Twitch_.Utils.get_twitch_file(BASE, message.room_id)
	file["games"] = file.get("games", False)
	if not file["games"]: return

	#make new game
	if not message.room_id in [game.room_id for game in active_battle_games]:

		ok = await BASE.moduls._Twitch_.Gold.edit_gold(BASE, message.room_id, message.user_id, "-", 200)
		if not ok: return

		new_game = battel_game(BASE, message.room_id, message.channel)

		new_game.fighter.append({"name": message.display_name, "_id": message.user_id})

		asyncio.ensure_future(new_game.start())
		active_battle_games.append(new_game)
		await BASE.Twitch_IRC_connection.send_message(message.channel, "Battle has been opend, type: \"!battle\" to join. (you need 200 Credits)")

	else:
		for game in active_battle_games:
			if message.room_id == game.room_id:
				if not game.active:
					if not game.warned:
						await BASE.Twitch_IRC_connection.send_message(message.channel, "The Arena is closed right now, visit again later")
						game.warned = True
					return

				#already in
				fighter_ = [f["_id"] for f in game.fighter]

				if message.user_id in fighter_:
					return

				else:
					ok = await BASE.moduls._Twitch_.Gold.edit_gold(BASE, message.room_id, message.user_id, "-", 200)
					if not ok:return
					game.fighter.append({"name": message.display_name, "_id": message.user_id})

class battel_game(object):
	def __init__(self, BASE, room_id, room_name):
		self.room_id = room_id
		self.room_name = room_name
		self.BASE = BASE
		self.fighter = []
		self.warned = False

		self.time_left = ( 60 * 2 )
		self.active = True
		self.timeout = ( 60 * 10 )

	async def start(self):
		while not self.time_left == 0:
			self.time_left -= 1
			await asyncio.sleep(1)
		await self.end()

	async def end(self):
		self.active = False
		winner = random.choice(self.fighter)
		win = len(self.fighter) * 200

		await self.BASE.moduls._Twitch_.Gold.edit_gold(self.BASE, self.room_id, winner["_id"], "+", win)
		await self.BASE.Twitch_IRC_connection.send_message(self.room_name, "The fight is over, the winner is: {0}, Congratulation! You won {1} Credits.".format(winner["name"], str(win)))
		while not self.timeout == 0:
			self.timeout -= 1
			await asyncio.sleep(1)
		await self.BASE.Twitch_IRC_connection.send_message(self.room_name, "The Arena has opened again and waits for new fighter. | !battle")
		active_battle_games.remove(self)

"""Mission Game"""
async def mission(BASE, message):
	file = await BASE.moduls._Twitch_.Utils.get_twitch_file(BASE, message.room_id)
	file["games"] = file.get("games", False)
	if not file["games"]: return

	#get bet
	m = message.content.split(" ")
	if len(m) == 1:
		return
	bet = m[1]
	if not bet.isdigit(): return
	bet = int(bet)

	#exist or new
	if bet == 0:
		return
	#new
	if not message.room_id in [game.room_id for game in active_missions]:

		ok = await BASE.moduls._Twitch_.Gold.edit_gold(BASE, message.room_id, message.user_id, "-", bet)
		if not ok: return

		new_game = mission_game(BASE, message.room_id, message.channel)

		new_game.fighter.append({"name": message.display_name, "_id": message.user_id, "amount": bet})

		asyncio.ensure_future(new_game.start())
		active_missions.append(new_game)
		await BASE.Twitch_IRC_connection.send_message(message.channel, "{0} is looking for fellows for a dangerous mission, you might die or come back with a lot of loot. Type: \"!mission [Credits]\" to join. ".format(message.save_name))

	#exist
	else:
		for game in active_missions:
			if message.room_id == game.room_id:
				if not game.active:
					if not game.warned:
						await BASE.Twitch_IRC_connection.send_message(message.channel, "No Missions available, visit again later")
						game.warned = True
					return

				#already in
				fighter_ = [f["_id"] for f in game.fighter]

				if message.user_id in fighter_:
					return

				else:
					ok = await BASE.moduls._Twitch_.Gold.edit_gold(BASE, message.room_id, message.user_id, "-", bet)
					if not ok:return
					game.fighter.append({"name": message.display_name, "_id": message.user_id, "amount": bet})

class mission_game(object):
	def __init__(self, BASE, room_id, room_name):
		self.room_id = room_id
		self.room_name = room_name
		self.BASE = BASE
		self.fighter = []
		self.winner = []
		self.warned = False

		self.time_left = ( 60 * 2 )
		self.active = True
		self.timeout = ( 60 * 10 )

	async def start(self):
		while not self.time_left == 0:
			self.time_left -= 1
			await asyncio.sleep(1)
		await self.end()

	async def end(self):
		self.active = False

		win_or_lose = [True, True, True, False, False, False, True]
		for player in self.fighter:
			if random.choice(win_or_lose):
				success = await self.BASE.moduls._Twitch_.Gold.edit_gold(
											self.BASE,
											self.room_id,
											player["_id"],
											"+",
											int(player["amount"] * 1.6))
				if not success:
					raise
				self.winner.append(player)
		#dead
		if len(self.winner) == 0:
			await self.BASE.Twitch_IRC_connection.send_message(self.room_name, "Mission failed ! | The fights were too rough and everyone was lost.")

		#all
		elif len(self.winner) == len(self.fighter):
			annc = ", ".join(f["name"] + " [" + str(int(f["amount"] * 1.5)) + "]" for f in self.winner)
			await self.BASE.Twitch_IRC_connection.send_message(self.room_name, "Mission success ! | The fights were rough, but everyone came back in one piece | They also brought some loot with them: {0}".format(annc))

		#announce
		else:
			annc = ", ".join(f["name"] + " [" + str(int(f["amount"] * 1.5)) + "]" for f in self.winner)
			await self.BASE.Twitch_IRC_connection.send_message(self.room_name, "Mission success ! | The fights were rough and some were lost | The rest brought some loot with them: {0}".format(annc))

		while not self.timeout == 0:
			self.timeout -= 1
			await asyncio.sleep(1)
		await self.BASE.Twitch_IRC_connection.send_message(self.room_name, "New Missions are available, are you ready for more awesome loot? | !mission [Credits]")
		active_missions.remove(self)
