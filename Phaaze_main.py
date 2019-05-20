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

################################################################################
# All threads for all platforms
################################################################################

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
