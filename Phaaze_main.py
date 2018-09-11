import time
import asyncio
import threading
import traceback
import PhaazeDBC as PhaazeDB
from importlib import reload

class BASE(object):
	""" contains everything, does everything, is everything -> can be found anywhere """
	def __init__(self, config=dict()):
		self.config = config
		self.version = config.get('version', '[N/A]')
		self.version_nr = ">help | v" + self.version
		self.uptime_var_1 = time.time() # together with now(), used to know how long phaaze is running
		self.RELOAD = False # yeah... that thing, i maybe remove it, its the indicator to reload modules

		#all featured "superclasses" aka, stuff that makes calls to somewhere
		self.discord = None
		self.twitch = None

		#get the active/load class, aka, what sould get started
		self.active = self.ACTIVE(self.config['active'])

		#a class filled with permanent vars, mainly from external sources or whatever
		self.vars = self.VARS(self.config['vars'])

		#the key to... whatever, that will be needed to connect to everything thats not ourself
		self.access = self.ACCESS(self.config['access'])

		#that contains pretty much everything
		self.modules = self.MODULES()

		#the key to memory, to important for BASE.modules
		self.PhaazeDB = PhaazeDB.Connection(port=3000, token=self.access.PhaazeDB_token, exception_on_error=False)

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

			self.osu_irc = bool(config.get('osu_irc', False))

			self.twitter = bool(config.get('twitter', False))
			self.youtube = bool(config.get('youtube', False))

			self.osu = False #TODO: remove this
			self.ai  = False #TODO: remove this
			self.music = False #TODO: remove this

	class VARS(object): #BASE.vars
		def __init__(self, config):
			self.Logo = open("VARS/logo.txt", "r").read()
			self.PT = config.get('trigger', '>')
			self.developer_id = config.get('developer', []) #override id's for discord #TODO: remove this
			self.doujin_help = open("VARS/doujin_help.txt","r").read().format("<",self.PT) #TODO: remove this
			self.twitch_logo = "https://i.redditmedia.com/za3YAsq33WcZc66FVb1cBw6mY5EibKpD_5hfLz0AbaE.jpg?w=320&s=53cf0ff252d84c5bb460b6ec0b195504" #TODO: remove this

	class ACCESS(object): #BASE.access
		def __init__(self, config):
			self.Twitch_Admin_Token =  config.get('Twitch_Admin_Token', '')
			self.Twitch_API_Token = config.get('Twitch_API_Token', '')
			self.Twitch_IRC_Token = config.get('Twitch_IRC_Token', '')

			self.Discord_Phaaze = config.get('Discord_Phaaze', '')
			self.Discord_Pheeze = config.get('Discord_Pheeze', '')
			self.Discord_Phaaze_secret = config.get('Discord_Phaaze_secret', '')

			self.Osu_API_Token = config.get('Osu_API_Token', '')
			self.Osu_IRC_Token = config.get('Osu_IRC_Token', '')

			self.Cleverbot_Token = config.get('Cleverbot_Token', '')

			self.Mashape = config.get('Mashape', '') #i need this for..eee ... urban dict or so... dunno, remove someday

			self.PhaazeDB_token = config.get('PhaazeDB_token', '')

		class Twitter(object): #FIXME: <- i fucked up RREEEEEEEEEE
			api_token = open("ACCESS_DATA/twitter_api_token.txt", "r").read().replace("\n","")
			api_token_key = open("ACCESS_DATA/twitter_api_token_key.txt", "r").read().replace("\n","")
			consumer_key = open("ACCESS_DATA/twitter_consumer_key.txt", "r").read().replace("\n","")
			consumer_secret = open("ACCESS_DATA/twitter_consumer_secret.txt", "r").read().replace("\n","")

	class MODULES(object): #BASE.modules
		def __init__(self):
			pass

		class _Discord_(object):

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

			import _DISCORD_.Blacklist as Blacklist

			import _DISCORD_.Custom as Custom

			import _DISCORD_.Discord_Events as Discord_Events

			import _DISCORD_.Levels as Levels

			import _DISCORD_.Open_Channel as Open

			import _DISCORD_.Priv_Channel as Priv

			import _DISCORD_.Twitch as Twitch

			import _DISCORD_.Utils as Utils

		class _Osu_(object):
			import _OSU_.Base as Base

			import _OSU_.Osu_IRC as IRC

			import _OSU_.Utils as Utils

		class _Twitch_(object):
			import _TWITCH_.Alerts as Alerts

			import _TWITCH_.Base as Base

			import _TWITCH_.Blacklist as Blacklist

			import _TWITCH_.Custom as Custom

			import _TWITCH_.Games as Games

			import _TWITCH_.Level as Level

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

		class _YouTube_(object):
			pass

		import Console as Console

		import Utils as Utils

	def run_async(self, async_function, exc_loop=None):
		if async_function == None:
			raise AttributeError("Async Func. can't be 'None'")
		async def _call_from_async_executer(future, func):
			result = await func
			future.set_result(result)

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
#TODO:
configuration=dict(access=dict(),active=dict(web=True),vars=dict())


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
			BASE.discord.run(BASE.access.Discord_Pheeze)

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

			O_IRC_ = BASE.modules._Osu_.IRC._IRC_(BASE)
			self.loop.run_until_complete(O_IRC_.run())

		except Exception as e:
			BASE.modules.Console.ERROR("Osu! IRC crashed: "+str(e))
			traceback.print_exc()
			time.sleep(3)

_osu_irc_ = __OSU_IRC__()
######################################

class __TWITCH_ALERTS__(threading.Thread):
	def __init__(self):
		super(__TWITCH_ALERTS__, self).__init__()
		self.name = "T_Alerts"
		self.daemon = True
		self.loop = asyncio.new_event_loop()

	def run(self):
		asyncio.set_event_loop(self.loop)

		#init BASE.twitch_alert_obj
		BASE.modules._Twitch_.Alerts.Init_Main(BASE)
		self.loop.run_until_complete(BASE.modules._Twitch_.Alerts.Main.start())

_twitch_alerts_ = __TWITCH_ALERTS__()
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

async def thread_saving(_d_: __DISCORD__,
						_t_: __TWITCH_IRC__,
						_ta_: __TWITCH_ALERTS__,
						_o_: __OSU_IRC__,
						_web_:__WEB__,
						_worker_:__WORKER__):

	BASE.modules.Console.INFO("PhaazeOS Mainframe started -> Starting Threads...")
	while BASE.active.main:
		try:

			if BASE.active.twitch_alert:
				if not _ta_.isAlive():
					try:
						BASE.modules.Console.INFO("Starting Twitch Alerts loop")
						_ta_ = __TWITCH_ALERTS__()
						_ta_.start()
						BASE.Twitch_Alerts_loop = _ta_.loop
					except:
						BASE.modules.Console.CRITICAL("Restarting Twitch Alerts Thread failed.")
			else:
				pass

			if BASE.active.discord:
				if not _d_.isAlive():
					try:
						BASE.modules.Console.INFO("Booting Discord...")
						_d_ = __DISCORD__()
						_d_.start()
						BASE.Discord_loop = _d_.loop
					except:
						BASE.modules.Console.CRITICAL("Restarting Discord Thread failed.")
			else:
				pass

			if BASE.active.twitch_irc:
				if not _t_.isAlive():
					try:
						BASE.modules.Console.INFO("Booting Twitch IRC...")
						_t_ = __TWITCH_IRC__()
						_t_.start()
						BASE.Twitch_loop = _t_.loop
					except:
						BASE.modules.Console.CRITICAL("Restarting Twitch IRC Thread failed.")
			else:
				pass

			if BASE.active.osu_irc:
				if not _o_.isAlive():
					try:
						BASE.modules.Console.INFO("INFO", "Booting Osu IRC...")
						_o_ = __OSU_IRC__()
						_o_.start()
						BASE.Osu_loop = _o_.loop
					except:
						BASE.modules.Console.CRITICAL("Restarting Osu IRC Thread failed.")
			else:
				pass

			if BASE.active.web:
				if not _web_.isAlive():
					try:
						BASE.modules.Console.INFO("Booting PhaazeWeb...")
						_web_ = __WEB__()
						_web_.start()
						BASE.Web_loop = _web_.loop
					except:
						BASE.modules.Console.CRITICAL("Restarting PhaazeWeb Thread failed.")
			else:
				pass

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
			print("WARNING: FATAL ERROR IN PHAAZE-MAINFRAME")

	print("Thread saver stoped")

class secure_of_all_treads(threading.Thread):
	def __init__(self):
		super(secure_of_all_treads, self).__init__()
		self.name = "Saving"
		self.xloop = asyncio.new_event_loop()

	def run(self):
		asyncio.set_event_loop(self.xloop)
		while BASE.active.main:
			try:
				self.xloop.run_until_complete(thread_saving(
									_discord_,
									_twitch_irc_,
									_twitch_alerts_,
									_osu_irc_,
									_web_,
									_worker_
									))
			except:
				print("WARNING: FATAL ERROR IN PHAAZE-MAINFRAME")

secure = secure_of_all_treads()
secure.start()
