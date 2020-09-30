from typing import TYPE_CHECKING, Coroutine
if TYPE_CHECKING:
	from main import Phaazebot

import threading
import asyncio
import traceback
import discord

MAINTHREAD_RELOAD_DELAY = 5 # in seconds

class Mainframe(threading.Thread):
	""" thread starter, that runs all other modules and secures that they are running while active state """
	def __init__(self, BASE:"Phaazebot"):
		super().__init__()
		self.BASE:"Phaazebot" = BASE
		self.name:str = "Mainframe"
		self.loop:asyncio.AbstractEventLoop = asyncio.new_event_loop()

		# a new idea, current is the thread that is actully running, after its crashed, use tpl, to generate a new one
		# making it so and can be looped from a dict
		self.modules:dict = dict(
			worker = dict(current=WorkerThread(BASE), tpl=WorkerThread),
			web = dict(current=WebThread(BASE), tpl=WebThread),
			discord = dict(current=DiscordThread(BASE), tpl=DiscordThread),
			twitch_irc = dict(current=TwitchThread(BASE), tpl=TwitchThread),
			twitch_events = dict(current=TwitchEventsThread(BASE), tpl=TwitchEventsThread),
			osu_irc = dict(current=OsuThread(BASE), tpl=OsuThread),
		)

	def run(self) -> None:
		while self.BASE.Active.main:
			try:
				self.loop.run_until_complete(self.secureModules())

			except KeyboardInterrupt:
				break

			except Exception as e:
				self.BASE.Logger.critical(f"FATAL ERROR IN MAINFRAME SECURE LOOP: {str(e)}")

	async def secureModules(self) -> None:
		while self.BASE.Active.main:

			for module_name in self.modules:
				PhaazeModule:threading.Thread = self.modules[module_name]["current"]

				# get from Phaazebot.Active if the module should be started or not
				start:bool = bool( getattr(self.BASE.Active, module_name.lower(), False) )
				if module_name.lower() == "worker": start = True # exception for worker, that always run

				if not PhaazeModule.is_alive() and start:
					self.BASE.Logger.info(f"Booting Thread: {PhaazeModule.name}")
					self.modules[module_name]["current"] = (self.modules[module_name]["tpl"])(self.BASE)
					self.modules[module_name]["current"].start()

			await asyncio.sleep(MAINTHREAD_RELOAD_DELAY)

class WorkerThread(threading.Thread):
	def __init__(self, BASE:"Phaazebot"):
		super().__init__()
		self.BASE:"Phaazebot" = BASE
		self.name:str = "Worker"
		self.daemon:bool = True
		self.loop:asyncio.AbstractEventLoop = asyncio.new_event_loop()

	async def sleepy(self) -> None:
		while 1: await asyncio.sleep(0.005)

	def run(self) -> None:
		try:
			asyncio.set_event_loop(self.loop)
			asyncio.ensure_future(self.sleepy())

			self.BASE.WorkerLoop = self.loop

			self.BASE.Logger.info(f"Started Worker Thread")
			self.loop.run_forever()

		except Exception as e:
			self.BASE.Logger.critical(f"Worker Thread crashed: {str(e)}")
			traceback.print_exc()

class DiscordThread(threading.Thread):
	def __init__(self, BASE:"Phaazebot"):
		super().__init__()
		self.BASE:"Phaazebot" = BASE
		self.name:str = "Discord"
		self.daemon:bool = True
		self.Loop:asyncio.AbstractEventLoop = asyncio.new_event_loop()

	def run(self) -> None:
		try:
			asyncio.set_event_loop(self.Loop)
			from Platforms.Discord.main_discord import PhaazebotDiscord

			# set loop in main object
			self.BASE.DiscordLoop = self.Loop

			# generate discord object
			self.BASE.Discord = PhaazebotDiscord(
				self.BASE,
				loop = self.Loop
			)

			# reset ready state, if not already
			self.BASE.IsReady.discord = False

			# generate coro
			DiscordCoro:Coroutine = self.BASE.Discord.start(
				self.BASE.Access.discord_token,
				reconnect=True
			)
			# let's go
			# sadly because of signal handler like SIGTERM etc, discord must be started via .start and not .run
			self.Loop.run_until_complete( DiscordCoro )

			# we only reach this point when discord is ended gracefull
			# which means a wanted disconnect,
			# else it will always call a exception
			self.BASE.Logger.info("Discord disconnected")

		except discord.errors.LoginFailure as LoginFail:
			self.BASE.Logger.critical(f"Unable to start Discord: {str(LoginFail)}")
			self.BASE.Active.discord = False

		except Exception as e:
			self.BASE.Logger.error(f"Discord Thread crashed: {str(e)}")
			traceback.print_exc()

class WebThread(threading.Thread):
	def __init__(self, BASE:"Phaazebot"):
		super().__init__()
		self.BASE:"Phaazebot" = BASE
		self.name:str = "Web"
		self.daemon:bool = True
		self.loop:asyncio.AbstractEventLoop = asyncio.new_event_loop()

	def run(self) -> None:
		try:
			asyncio.set_event_loop(self.loop)
			from Platforms.Web.main_web import PhaazebotWeb

			self.BASE.Web = PhaazebotWeb(self.BASE)
			self.BASE.WebLoop = self.loop

			self.BASE.Web.start() # blocking call, takes asyncio.loop

			# we only reach this point when the webserver is ended gracefull
			self.BASE.Logger.info("Web server shutdown")

		except Exception as e:
			self.BASE.Logger.error(f"Web Thread crashed: {str(e)}")
			traceback.print_exc()

class OsuThread(threading.Thread):
	def __init__(self, BASE:"Phaazebot"):
		super().__init__()
		self.BASE:"Phaazebot" = BASE
		self.name:str = "Osu"
		self.daemon:bool = True
		self.Loop:asyncio.AbstractEventLoop = asyncio.new_event_loop()

	def run(self) -> None:
		try:
			asyncio.set_event_loop(self.Loop)
			from Platforms.Osu.main_osu import PhaazebotOsu

			# set loop in main object
			self.BASE.OsuLoop = self.Loop

			# generate osu! object
			self.BASE.Osu = PhaazebotOsu(
				self.BASE,
				Loop = self.Loop,
				token = self.BASE.Access.osu_irc_token,
				nickname = self.BASE.Access.osu_irc_nickname
			)

			# reset ready state, if not already
			self.BASE.IsReady.osu = False

			# let's go
			self.BASE.Osu.run()

			# we only should reach this point when osu is ended gracefull
			# which means a wanted disconnect,
			# else it will always call a exception
			self.BASE.Logger.info("Osu disconnected")

		except Exception as e:
			self.BASE.Logger.error(f"Osu Thread crashed: {str(e)}")
			traceback.print_exc()

class TwitchEventsThread(threading.Thread):
	def __init__(self, BASE:"Phaazebot"):
		super().__init__()
		self.BASE:"Phaazebot" = BASE
		self.name:str = "Twitch Events"
		self.daemon:bool = True
		self.loop:asyncio.AbstractEventLoop = asyncio.new_event_loop()

	def run(self) -> None:
		try:
			asyncio.set_event_loop(self.loop)
			from Platforms.Twitch.main_events import PhaazebotTwitchEvents

			self.BASE.TwitchEvents = PhaazebotTwitchEvents(self.BASE)
			self.BASE.TwitchEventsLoop = self.loop

			self.loop.run_until_complete( self.BASE.TwitchEvents.start() )

			# we only should reach this point when it's ended gracefull
			# else it will always call a exception
			self.BASE.Logger.info("Twitch Events stopped")

		except Exception as e:
			self.BASE.Logger.error(f"Twitch Events Thread crashed: {str(e)}")
			traceback.print_exc()

class TwitchThread(threading.Thread):
	def __init__(self, BASE:"Phaazebot"):
		super().__init__()
		self.BASE:"Phaazebot" = BASE
		self.name:str = "Twitch"
		self.daemon:bool = True
		self.Loop:asyncio.AbstractEventLoop = asyncio.new_event_loop()

	def run(self) -> None:
		try:
			asyncio.set_event_loop(self.Loop)
			from Platforms.Twitch.main_twitch import PhaazebotTwitch

			# set loop in main object
			self.BASE.TwitchLoop = self.Loop

			# generate Twitch object
			self.BASE.Twitch = PhaazebotTwitch(
				self.BASE,
				Loop = self.Loop,
				token = self.BASE.Access.twitch_irc_token,
				nickname = self.BASE.Access.twitch_irc_nickname,
			)

			# reset ready state, if not already
			self.BASE.IsReady.twitch = False

			# let's go
			self.BASE.Twitch.run()

			# we only should reach this point when twitch is ended gracefull
			# which means a wanted disconnect,
			# else it will always call a exception
			self.BASE.Logger.info("Twitch disconnected")

		except Exception as e:
			self.BASE.Logger.error(f"Twitch Thread crashed: {str(e)}")
			traceback.print_exc()
