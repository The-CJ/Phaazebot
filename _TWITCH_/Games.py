#BASE.modules._Twitch_.Games

import asyncio, random

active_battle_games = []
active_missions = []

class Battle(object):

	active_battles = []

	async def Base(BASE, message, kwargs):
		channel_settings = kwargs.get('channel_settings', None)
		if channel_settings == None:
			channel_settings = await BASE.modules._Twitch_.Utils.get_channel_settings(BASE, message.channel_id)
			kwargs['channel_settings'] = channel_settings

		if not channel_settings.get('active_games', False): return

		battle = Battle.get_battle(message.channel_id)

		if battle == None: return await Battle.new_game(BASE, message, kwargs)
		elif battle.finished: await battle.warn()
		else: return await Battle.add_fighter(BASE, message, battle, kwargs)

	async def new_game(BASE, message, kwargs):
		# only start new game if invoker has enough gold
		has_enough = await BASE.modules._Twitch_.Utils.edit_currency(BASE, channel_id=message.channel_id, user_id=message.user_id, change=-200)
		if not has_enough: return

		# generate battle
		new_game = BattleObject(BASE, message.channel)
		new_game.fighter.append(Battle.Fighter(message.author))

		# start timer and append as active
		asyncio.ensure_future(new_game.start())
		Battle.active_battles.append(new_game)

		currency_name_multi = kwargs.get('channel_settings', dict()).get("currency_name_multi", BASE.vars.DEFAULT_TWITCH_CURRENCY_MULTI)
		return await BASE.twitch.send_message(
			message.channel_name,
			f'Battle has been opened, type: "{BASE.vars.TRIGGER_TWITCH}battle" to join. (you need 200 {currency_name_multi})'
		)

	async def add_fighter(BASE, message, battle, kwargs):
		#already in?
		check = Battle.get_fighter(battle, message.user_id)
		if check != None: return

		#can afford?
		has_enough = await BASE.modules._Twitch_.Utils.edit_currency(BASE, channel_id=message.channel_id, user_id=message.user_id, change=-200)
		if not has_enough: return

		battle.fighter.append(Battle.Fighter(message.author))

	class Fighter(object):
		def __init__(self, author):
			self.display_name = author.display_name
			self.user_id = author.id

	def get_fighter(battle, search_id):
		for Fighter in battle.fighter:
			if str(Fighter.user_id) == str(search_id): return Fighter
		return None

	def get_battle(search_id):
		for CheckBattle in Battle.active_battles:
			if str(CheckBattle.channel.id) == str(search_id): return CheckBattle
		return None

async def Mission(BASE, message, kwargs):
	file = await BASE.modules._Twitch_.Utils.get_twitch_file(BASE, message.room_id)
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

		ok = await BASE.modules._Twitch_.Gold.edit_gold(BASE, message.room_id, message.user_id, "-", bet)
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
					ok = await BASE.modules._Twitch_.Gold.edit_gold(BASE, message.room_id, message.user_id, "-", bet)
					if not ok:return
					game.fighter.append({"name": message.display_name, "_id": message.user_id, "amount": bet})

class BattleObject(object):
	def __init__(self, BASE, channel):
		self.BASE = BASE
		self.channel = channel
		self.fighter = []

		self.warned = False
		self.finished = False

		self.time_left = ( 60 * 2 )
		self.timeout = ( 60 * 10 )

	async def start(self):
		while not self.time_left == 0:
			self.time_left -= 1
			await asyncio.sleep(1)
		await self.end()

	async def end(self):
		self.finished = True
		winner = random.choice(self.fighter)
		win = len(self.fighter) * 200

		await self.BASE.modules._Twitch_.Utils.edit_currency(self.BASE, self.channel.id, winner.user_id, win)
		await self.BASE.twitch.send_message(
			self.channel.name,
			f"The fight is over, the winner is: {winner.display_name}, Congratulation! You won {win} Credits."
		)
		await self.cooldown()

	async def warn(self):
		if self.warned: return
		self.warned = True
		await self.BASE.twitch.send_message(
			self.channel.name,
			f"The Arena is closed right now, visit again later"
		)

	async def cooldown(self):
		while not self.timeout == 0:
			self.timeout -= 1
			await asyncio.sleep(1)
		await self.BASE.twitch.send_message(
			self.channel.name,
			f"The Arena has opened again and waits for new fighter. | {self.BASE.vars.TRIGGER_TWITCH}battle"
		)
		Battle.active_battles.remove(self)
