import time, json
import asyncio
import threading
import traceback
import PhaazeDBC as PhaazeDB
from Utils import CLI_Args

class BASE(object):
	""" contains everything, does everything, is everything -> can be found anywhere """
	def __init__(self, config = dict()):
		self.config = config
		self.version = config.get('version', '[N/A]')
		self.uptime_var_1 = time.time() # together with now(), used to know how long phaaze is running
		self.RELOAD = False # yeah... that thing, i maybe remove it, its the indicator to reload modules

		#all featured "superclasses" aka, stuff that makes calls to somewhere
		self.discord = None
		self.twitch = None
		self.osu = None

		#get the active/load class, aka, what sould get started
		self.active = self.ACTIVE( self.config.get('active', dict()) )

		#a class filled with permanent vars, mainly from external sources or whatever
		self.vars = self.VARS( self.config.get('vars', dict()) )

		#the key to... whatever, that will be needed to connect to everything thats not ourself
		self.access = self.ACCESS( self.config.get('access', dict()) )

		#contains user limits for all addeble things, like custom command amount
		self.limit = self.LIMIT( self.config.get('limit', dict()) )

		#that contains pretty much everything
		self.modules = self.MODULES()

		#the key to memory, to important for BASE.modules
		self.PhaazeDB = PhaazeDB.Connection(port=3000, token=self.access.PhaazeDB_token, exception_on_error=True)

	class is_ready(object):
		#all start False, turn True when connected
		discord = False
		twitch = False
		osu = False
		twitter = False
		youtube = False

	class ACTIVE(object): #BASE.active
		def __init__(self, config):
			self.main = bool(config.get('main', True))
			self.api = bool(config.get('api', False))
			self.web = bool(config.get('web', False))

			self.discord = bool(config.get('discord', False))
			self.twitch_irc = bool(config.get('twitch_irc', False))
			self.twitch_alert = bool(config.get('twitch_alert', False))
			self.twitch_stream = bool(config.get('twitch_stream', False))

			self.osu_irc = bool(config.get('osu_irc', False))

			self.twitter = bool(config.get('twitter', False))
			self.youtube = bool(config.get('youtube', False))

			self.osu = False #TODO: remove this
			self.ai  = False #TODO: remove this
			self.music = False #TODO: remove this

	class VARS(object): #BASE.vars
		def __init__(self, config):
			self.Logo = open("VARS/logo.txt", "r").read()

			self.TRIGGER_DISCORD = config.get('trigger_discord', '>')
			self.TRIGGER_OSU = config.get('trigger_osu', '!')
			self.TRIGGER_TWITCH = config.get('trigger_twitch', '!')

			self.DEFAULT_TWITCH_CURRENCY = config.get('default_twitch_currency', 'Credit')
			self.DEFAULT_TWITCH_CURRENCY_MULTI = config.get('default_twitch_currency_multi', 'Credits')

			self.osu_logo = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Osu%21Logo_%282015%29.png/600px-Osu%21Logo_%282015%29.png"
			self.twitch_logo = "https://i.redditmedia.com/za3YAsq33WcZc66FVb1cBw6mY5EibKpD_5hfLz0AbaE.jpg?w=320&s=53cf0ff252d84c5bb460b6ec0b195504" #TODO: remove this

			self.developer_id = config.get('developer', []) #override id's for discord #TODO: remove this
			self.doujin_help = open("VARS/doujin_help.txt","r").read().format("<",self.TRIGGER_DISCORD) #TODO: remove this

	class ACCESS(object): #BASE.access
		def __init__(self, config):
			self.Twitch_Admin_Token = config.get('Twitch_Admin_Token', '')
			self.Twitch_API_Token = config.get('Twitch_API_Token', '')
			self.Twitch_IRC_Token = config.get('Twitch_IRC_Token', '')

			self.Discord = config.get('Discord', '')

			self.Osu_API_Token = config.get('Osu_API_Token', '')
			self.Osu_IRC_Token = config.get('Osu_IRC_Token', '')

			self.Cleverbot_Token = config.get('Cleverbot_Token', '')

			self.Mashape = config.get('Mashape', '') #i need this for..eee ... urban dict or so... dunno, remove someday

			self.PhaazeDB_token = config.get('PhaazeDB_token', '')

			self.twitter_token = config.get('twitter_token','')
			self.twitter_token_key = config.get('twitter_token_key','')
			self.twitter_consumer_key = config.get('twitter_consumer_key','')
			self.twitter_consumer_secret = config.get('twitter_consumer_secret','')

	class LIMIT(object): #BASE.limit
		def __init__(self, config):
			self.DISCORD_PRIVATE_COOLDOWN = config.get("discord_private_cooldown", 1)
			self.DISCORD_NORMAL_COOLDOWN = config.get("discord_normal_cooldown", 1)
			self.DISCORD_MOD_COOLDOWN = config.get("discord_mod_cooldown", 3)
			self.DISCORD_OWNER_COOLDOWN = config.get("discord_owner_cooldown", 5)
			self.DISCORD_CUSTOM_COMAMNDS_AMOUNT = config.get("discord_custom_commands_amount", 100)
			self.DISCORD_CUSTOM_COMMANDS_COOLDOWN = config.get("discord_custom_commands_cooldown", 3)
			self.DISCORD_LEVEL_COOLDOWN = config.get("discord_level_cooldown", 3)
			self.DISCORD_QUOTES_AMOUNT = config.get("discord_quotes_amount", 100)
			self.DISCORD_ADDROLE_AMOUNT = config.get("discord_addrole_amount", 25)

			self.TWITCH_TIMEOUT_MESSAGE_COOLDOWN = config.get("twitch_timeout_message_cooldown", 20)
			self.TWITCH_BLACKLIST_REMEMBER_TIME = config.get("twitch_blacklist_remember_time", 180)
			self.TWITCH_CUSTOM_COMMAND_AMOUNT = config.get("twitch_custom_command_amount", 100)
			self.TWITCH_QUOTE_AMOUNT = config.get("twitch_quote_amount", 100)
			self.TWITCH_STATS_COOLDOWN = config.get("twitch_stats_cooldown", 5)

			self.WEB_CLIENT_MAX_SIZE = config.get("web_client_max_size", 5242880) #5MB

	class MODULES(object): #BASE.modules
		def __init__(self):
			pass

		class _Discord_(object):

			import _DISCORD_.Blacklist as Blacklist

			import _DISCORD_.Custom as Custom

			import _DISCORD_.Discord_Events as Discord_Events

			import _DISCORD_.Levels as Levels

			import _DISCORD_.Open_Channel as Open

			import _DISCORD_.Priv_Channel as Priv

			import _DISCORD_.Twitch as Twitch

			import _DISCORD_.Utils as Utils

			class CMD(object):
				import _DISCORD_.CMD.Normal as Normal

				import _DISCORD_.CMD.Mod as Mod

				import _DISCORD_.CMD.Owner as Owner

				import _DISCORD_.CMD.Dev as Dev

			class PROCESS(object):
				import _DISCORD_.PROCESS.Normal as Normal

				import _DISCORD_.PROCESS.Mod as Mod

				import _DISCORD_.PROCESS.Owner as Owner

				import _DISCORD_.PROCESS.Dev as Dev

		class _Osu_(object):
			import _OSU_.Base as Base

			import _OSU_.Utils as Utils

			class CMD():
				import _OSU_.CMD.Normal as Normal

			class PROCESS():
				import _OSU_.PROCESS.Normal as Normal

		class _Twitch_(object):
			import _TWITCH_.Base as Base

			import _TWITCH_.Blacklist as Blacklist

			import _TWITCH_.Custom as Custom

			import _TWITCH_.Games as Games

			import _TWITCH_.Level as Level

			import _TWITCH_.Lurker as Lurker

			import _TWITCH_.Streams as Streams

			import _TWITCH_.Utils as Utils

			class CMD(object):
				import _TWITCH_.CMD.Normal as Normal

				import _TWITCH_.CMD.Mod as Mod

				import _TWITCH_.CMD.Owner as Owner

			class PROCESS(object):
				import _TWITCH_.PROCESS.Normal as Normal

				import _TWITCH_.PROCESS.Mod as Mod

				import _TWITCH_.PROCESS.Owner as Owner

		class _Twitter_(object):
			import _TWITTER_.Base as Base

		class _Web_(object):
			import _WEB_.Base as Base

			import _WEB_.Utils as Utils

			import _WEB_.Mail as Mail

		class _YouTube_(object):
			pass

		import Console as Console

		import Utils as Utils

	def run_async(self, async_function, exc_loop=None):
		if async_function == None:
			raise AttributeError("Async Func. can't be 'None'")
		async def _call_from_async_executer(future, func):
			try:
				result = await func
				future.set_result(result)
			except Exception as e:
				future.set_result(e)

		future = asyncio.Future()
		if exc_loop == None:
			exc_loop = self.Worker_loop
		asyncio.ensure_future(_call_from_async_executer( future, async_function ), loop=exc_loop)
		while not future.done():
			time.sleep(0.01)
		return future.result()

	def reload_base(self):
		pass
		#TODO:

	async def shutdown(self):
		"""Save programm shutdown"""

		for t in threading.enumerate():
			if hasattr(t, "loop"):
				print(str(t))
				try: t.loop.close()
				except: pass

		self.active.main = False

		self.active.discord = False
		self.active.twitch_irc = False
		self.active.twitch_alert = False
		self.active.osu_irc = False

		try: await self.phaaze.logout()
		except: pass

		print("PhaazeOS will be shutdown as soon as possible.")

#get config
if CLI_Args.get("no-args", False) == False:
	try:
		file_ = open("config.json", "r").read()
		structure = json.loads(file_)

	except json.decoder.JSONDecodeError:
		print('config.json could not be loaded, invalid json')
		structure=None

	except FileNotFoundError:
		print('config.json could not be read, no file found')
		structure=None

	except Exception as e:
		print('unknown error')
		print(str(e))
		structure=None

	finally:
		if structure == None: exit("PhaazeOS not started -> missing configuration")
		configuration = structure
else:
	print('Starting without configuration')
	configuration = dict()

#load it up
BASE = BASE(config=configuration)

################################################################################
# All threads for all platforms
################################################################################

class __WORKER__(threading.Thread):
	def __init__(self):
		super(__WORKER__, self).__init__()
		self.name = "Worker"
		self.daemon = True
		self.loop = asyncio.new_event_loop()

	def run(self):
		try:
			async def sleepy():
				while 1:
					await asyncio.sleep(0.005)

			asyncio.set_event_loop(self.loop)
			asyncio.ensure_future(sleepy())
			self.loop.run_forever()


		except Exception as e:
			BASE.modules.Console.ERROR("Worker crashed: "+str(e))
			traceback.print_exc()
			time.sleep(3)

_worker_ = __WORKER__()

######################################
class __DISCORD__(threading.Thread):
	def __init__(self):
		super(__DISCORD__, self).__init__()
		self.name = "Discord"
		self.daemon = True
		self.loop = asyncio.new_event_loop()

	def run(self):
		try:
			asyncio.set_event_loop(self.loop)

			from _DISCORD_.Main_discord import Init_discord
			BASE.discord = Init_discord(BASE)
			BASE.discord.run(BASE.access.Discord)

		except Exception as e:
			BASE.modules.Console.ERROR("Discord crashed: "+str(e))
			traceback.print_exc()
			time.sleep(3)

_discord_ = __DISCORD__()
######################################

class __TWITCH_IRC__(threading.Thread):
	def __init__(self):
		super(__TWITCH_IRC__, self).__init__()
		self.name = "T_IRC"
		self.daemon = True
		self.loop = asyncio.new_event_loop()

	def run(self):
		try:
			asyncio.set_event_loop(self.loop)

			from _TWITCH_.Main_twitch import Init_twitch
			BASE.twitch = Init_twitch(BASE)
			BASE.twitch.run(token=BASE.access.Twitch_IRC_Token, nickname="phaazebot")

		except Exception as e:
			BASE.modules.Console.ERROR("Twitch IRC crashed: "+ str(e))
			traceback.print_exc()
			time.sleep(3)

_twitch_irc_ = __TWITCH_IRC__()
######################################

class __OSU_IRC__(threading.Thread):
	def __init__(self):
		super(__OSU_IRC__, self).__init__()
		self.name = "O_IRC"
		self.daemon = True
		self.loop = asyncio.new_event_loop()

	def run(self):
		try:
			asyncio.set_event_loop(self.loop)

			from _OSU_.Main_osu import Init_osu
			BASE.osu = Init_osu(BASE)
			BASE.osu.run(token=BASE.access.Osu_IRC_Token, nickname="Phaazebot")

		except Exception as e:
			BASE.modules.Console.ERROR("Osu! IRC crashed: "+str(e))
			traceback.print_exc()
			time.sleep(3)

_osu_irc_ = __OSU_IRC__()
######################################

class __TWITCH_STREAMS__(threading.Thread):
	def __init__(self):
		super(__TWITCH_STREAMS__, self).__init__()
		self.name = "T_streams"
		self.daemon = True
		self.loop = asyncio.new_event_loop()

	def run(self):
		asyncio.set_event_loop(self.loop)

		Twitch_Streams = BASE.modules._Twitch_.Streams.Init_Main(BASE)
		BASE.modules._Twitch_.Streams.Main = Twitch_Streams
		self.loop.run_until_complete( BASE.modules._Twitch_.Streams.Main.start() )

_twitch_streams_ = __TWITCH_STREAMS__()
######################################

class __WEB__(threading.Thread):
	def __init__(self):
		super(__WEB__, self).__init__()
		self.name = "Web"
		self.daemon = True
		self.loop = asyncio.new_event_loop()

	def run(self):
		asyncio.set_event_loop(self.loop)

		self.loop.run_until_complete(BASE.modules._Web_.Base.webserver(BASE))

_web_ = __WEB__()
################################################################################

async def MAINFRAME_LOOP(_d_: __DISCORD__,
						_t_: __TWITCH_IRC__,
						_ts_: __TWITCH_STREAMS__,
						_o_: __OSU_IRC__,
						_web_:__WEB__,
						_worker_:__WORKER__):

	BASE.modules.Console.INFO("PhaazeOS Mainframe started -> Starting Threads...")
	while BASE.active.main:
		try:

			if BASE.active.twitch_stream:
				if not _ts_.isAlive():
					try:
						BASE.modules.Console.INFO("Starting Twitch Stream loop")
						_ts_ = __TWITCH_STREAMS__()
						_ts_.start()
						BASE.Twitch_Stream_loop = _ts_.loop
					except:
						BASE.modules.Console.CRITICAL("Restarting Twitch Stream Thread failed.")

			if BASE.active.discord:
				if not _d_.isAlive():
					try:
						BASE.modules.Console.INFO("Booting Discord...")
						_d_ = __DISCORD__()
						_d_.start()
						BASE.Discord_loop = _d_.loop
					except:
						BASE.modules.Console.CRITICAL("Restarting Discord Thread failed.")

			if BASE.active.twitch_irc:
				if not _t_.isAlive():
					try:
						BASE.modules.Console.INFO("Booting Twitch IRC...")
						_t_ = __TWITCH_IRC__()
						_t_.start()
						BASE.Twitch_loop = _t_.loop
					except:
						BASE.modules.Console.CRITICAL("Restarting Twitch IRC Thread failed.")

			if BASE.active.osu_irc:
				if not _o_.isAlive():
					try:
						BASE.modules.Console.INFO("Booting Osu IRC...")
						_o_ = __OSU_IRC__()
						_o_.start()
						BASE.Osu_loop = _o_.loop
					except:
						BASE.modules.Console.CRITICAL("Restarting Osu IRC Thread failed.")

			if BASE.active.web:
				if not _web_.isAlive():
					try:
						BASE.modules.Console.INFO("Booting PhaazeWeb...")
						_web_ = __WEB__()
						_web_.start()
						BASE.Web_loop = _web_.loop
					except:
						BASE.modules.Console.CRITICAL("Restarting PhaazeWeb Thread failed.")

			if not _worker_.isAlive():
				try:
					BASE.modules.Console.INFO("Booting Universal Async Worker...")
					_worker_ = __WORKER__()
					_worker_.start()
					BASE.Worker_loop = _worker_.loop
				except:
					BASE.modules.Console.CRITICAL("Restarting Worker Thread failed.")

			await asyncio.sleep(5)
		except:
			print("WARNING: FATAL ERROR IN PHAAZE-MAINFRAME LOOP")
			await asyncio.sleep(3)

	print("Thread saver stoped")

class MAINFRAME(threading.Thread):
	def __init__(self):
		super(MAINFRAME, self).__init__()
		self.name = "Mainframe"
		self.loop = asyncio.new_event_loop()

	def run(self):
		asyncio.set_event_loop(self.loop)
		while BASE.active.main:
			try:
				self.loop.run_until_complete(
					MAINFRAME_LOOP(
						_discord_,
						_twitch_irc_,
						_twitch_streams_,
						_osu_irc_,
						_web_,
						_worker_
					)
				)

			except KeyboardInterrupt:
				break

			except:
				print("WARNING: FATAL ERROR IN PHAAZE-MAINFRAME")

MAIN = MAINFRAME()

if __name__ == '__main__':
	MAIN.start()
