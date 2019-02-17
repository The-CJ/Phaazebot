#BASE.modules._Twitch_.Games

import asyncio, random

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

		channel_settings = kwargs.get('channel_settings', None)
		if channel_settings == None:
			channel_settings = await BASE.modules._Twitch_.Utils.get_channel_settings(BASE, message.channel_id)

		# generate battle
		battle = BattleObject(BASE, message.channel, channel_settings=channel_settings )
		battle.fighter.append(Battle.Fighter(message.author))

		# start timer and append as active
		asyncio.ensure_future(battle.start())
		Battle.active_battles.append(battle)

		return await BASE.twitch.send_message(
			message.channel_name,
			f'Battle has been opened, type: "{BASE.vars.TRIGGER_TWITCH}battle" to join. (you need 200 {battle.currency_name_multi})'
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

class Mission(object):

	active_missions = []

	async def Base(BASE, message, kwargs):
		channel_settings = kwargs.get('channel_settings', None)
		if channel_settings == None:
			channel_settings = await BASE.modules._Twitch_.Utils.get_channel_settings(BASE, message.channel_id)
			kwargs['channel_settings'] = channel_settings

		if not channel_settings.get('active_games', False): return

		mission = Mission.get_mission(message.channel_id)

		if mission == None: return await Mission.new_game(BASE, message, kwargs)
		elif mission.finished: await mission.warn()
		else: return await Mission.add_adventurer(BASE, message, mission, kwargs)

	async def new_game(BASE, message, kwargs):

		bet = Mission.get_bet(message)
		if not bet: return

		has_enough = await BASE.modules._Twitch_.Utils.edit_currency(BASE, channel_id=message.channel_id, user_id=message.user_id, change=(bet*-1))
		if not has_enough: return

		channel_settings = kwargs.get('channel_settings', None)
		if channel_settings == None:
			channel_settings = await BASE.modules._Twitch_.Utils.get_channel_settings(BASE, message.channel_id)

		mission = MissionObject(BASE, message.channel, channel_settings=channel_settings)

		mission.adventurers.append(Mission.Adventurer(message.author, bet))

		asyncio.ensure_future(mission.start())
		Mission.active_missions.append(mission)

		return await BASE.twitch.send_message(
			message.channel_name,
			f'{message.author.display_name} is looking for fellows for a dangerous mission,'\
			f' you might die or come back with a lot of loot. Type: "{BASE.vars.TRIGGER_TWITCH}mission [amount]" to join.')

	async def add_adventurer(BASE, message, mission, kwargs):
		#already in?
		check = Mission.get_adventurer(mission, message.user_id)
		if check != None: return

		bet = Mission.get_bet(message)
		if not bet: return

		#can afford?
		has_enough = await BASE.modules._Twitch_.Utils.edit_currency(BASE, channel_id=message.channel_id, user_id=message.user_id, change=(bet*-1))
		if not has_enough: return

		mission.adventurers.append(Mission.Adventurer(message.author, bet))

	class Adventurer(object):
		def __init__(self, author, amount):
			self.display_name = author.display_name
			self.user_id = author.id
			self.amount = amount

	def get_bet(message):
		m = message.content.split(" ")
		if len(m) < 2: return False
		bet = m[1]
		if not bet.isdigit(): return False
		bet = int(bet)
		if bet <= 0: return False
		return bet

	def get_adventurer(mission, search_id):
		for Adventurer in mission.adventurers:
			if str(Adventurer.user_id) == str(search_id): return Adventurer
		return None

	def get_mission(search_id):
		for CheckMission in Mission.active_missions:
			if str(CheckMission.channel.id) == str(search_id): return CheckMission
		return None

class BattleObject(object):
	def __init__(self, BASE, channel, channel_settings = dict()):
		self.BASE = BASE
		self.channel = channel
		self.fighter = []

		self.currency_name = channel_settings.get('currency_name', self.BASE.vars.DEFAULT_TWITCH_CURRENCY) or self.BASE.vars.DEFAULT_TWITCH_CURRENCY
		self.currency_name_multi = channel_settings.get('currency_name_multi', self.BASE.vars.DEFAULT_TWITCH_CURRENCY_MULTI) or self.BASE.vars.DEFAULT_TWITCH_CURRENCY_MULTI

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
			f"The fight is over, the winner is: {winner.display_name}, Congratulation! You won {win} {self.currency_name_multi}."
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

class MissionObject(object):
	def __init__(self, BASE, channel, channel_settings = dict()):
		self.BASE = BASE
		self.channel = channel
		self.adventurers = []
		self.winner = []

		self.currency_name = channel_settings.get('currency_name', self.BASE.vars.DEFAULT_TWITCH_CURRENCY) or self.BASE.vars.DEFAULT_TWITCH_CURRENCY
		self.currency_name_multi = channel_settings.get('currency_name_multi', self.BASE.vars.DEFAULT_TWITCH_CURRENCY_MULTI) or self.BASE.vars.DEFAULT_TWITCH_CURRENCY_MULTI

		self.warned = False
		self.finished = False

		self.time_left = ( 60 * 2 )
		self.timeout = ( 60 * 10 )
		self.win_chance = 0.625

	async def start(self):
		while not self.time_left == 0:
			self.time_left -= 1
			await asyncio.sleep(1)
		await self.end()

	async def end(self):
		self.finished = True

		for Adventurer in self.adventurers:
			if random.random() < self.win_chance:
				await self.BASE.modules._Twitch_.Utils.edit_currency(
					self.BASE,
					channel_id=self.channel.id,
					user_id=Adventurer.user_id,
					change=int(Adventurer.amount*1.5)
				)
				self.winner.append(Adventurer)

		if len(self.winner) == 0:
			await self.BASE.twitch.send_message(self.channel.name, "Mission failed! | The fights were to rough and everyone was lost...")

		elif len(self.winner) == len(self.adventurers):
			rep_addition = ", ".join(f"[{w.display_name} +{int(w.amount*1.5)}]" for w in self.winner)
			rep_message = "Mission success! | The fights were rough, but everyone came back in one piece and got some loot: " + rep_addition
			await self.BASE.twitch.send_message(self.channel.name, rep_message)

		else:
			rep_addition = ", ".join(f"[{w.display_name} +{int(w.amount*1.5)}]" for w in self.winner)
			rep_message = "Mission success! | The fights were rough and some gone lost, the rest brought some loot back: " + rep_addition
			await self.BASE.twitch.send_message(self.channel.name, rep_message)

		await self.cooldown()

	async def warn(self):
		if self.warned: return
		self.warned = True
		await self.BASE.twitch.send_message(
			self.channel.name,
			f"No Missions available, visit again later"
		)

	async def cooldown(self):
		while not self.timeout == 0:
			self.timeout -= 1
			await asyncio.sleep(1)
		await self.BASE.twitch.send_message(
			self.channel.name,
			f"New missions are avariable, are you ready for more awesome loot? | {self.BASE.vars.TRIGGER_TWITCH}mission [amount]"
		)
		Mission.active_missions.remove(self)
