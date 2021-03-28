from typing import Optional
import asyncio
import time

from Utils.Classes.storeclasses import (
	ActiveStore,
	VarsStore,
	AccessStore,
	LimitStore,
	IsReadyStore,
	GlobalStorage
)
from Utils.config import ConfigParser
from Utils.logger import PhaazeLogger
from Utils.threads import Mainframe as MainframeThread
from Utils.Classes.dbconn import DBConn
from Utils.startuptastk import initStartupTasks
from Utils.cli import CliArgs

# platforms
from Platforms.Discord.main_discord import PhaazebotDiscord
from Platforms.Web.main_web import PhaazebotWeb
from Platforms.Osu.main_osu import PhaazebotOsu
from Platforms.Twitch.main_twitch import PhaazebotTwitch
from Platforms.Twitch.main_events import PhaazebotTwitchEvents

class Phaazebot(object):
	"""
	main class containing all other information.
	that's phaaze
	"""
	def __init__(self, PreConfig:ConfigParser=None):

		if PreConfig:
			self.Config:ConfigParser = PreConfig
		else:
			cfg_path:str = CliArgs.get("config_path", "Config/config.phzcf")
			cfg_type:str = CliArgs.get("config_type", "phzcf")
			self.Config:ConfigParser = ConfigParser(file_path=cfg_path, file_type=cfg_type)

		self.version:str = self.Config.get("version", "[N/A]")
		self.start_time:float = time.time() # together with another time.time(), used to know how long phaaze is running

		# log to handler of choice
		self.Logger:PhaazeLogger = PhaazeLogger()

		# get the active/load class, aka, what should get started
		self.Active:ActiveStore = ActiveStore(self)

		# a class filled with permanent vars, mainly from external sources or whatever
		self.Vars:VarsStore = VarsStore(self)

		# the key to everything, that will be needed to connect to everything that's not ourself
		self.Access:AccessStore = AccessStore(self)

		# contains user limits for all addable things, like custom command amount
		self.Limit:LimitStore = LimitStore(self)

		# all featured "superclasses" aka, stuff that makes calls to somewhere
		# all of these get added by self.Mainframe when started
		# both the actual working part and a quick link to there running loops, to inject async functions for them to run
		# most likely used for the worker, that can calculate time consuming functions or discord because send_message must be called from this loop
		self.Discord:PhaazebotDiscord = PhaazebotDiscord(self)
		self.DiscordLoop:Optional[asyncio.AbstractEventLoop] = None

		self.Twitch:PhaazebotTwitch = PhaazebotTwitch(self)
		self.TwitchLoop:Optional[asyncio.AbstractEventLoop] = None

		self.TwitchEvents:PhaazebotTwitchEvents = PhaazebotTwitchEvents(self)
		self.TwitchEventsLoop:Optional[asyncio.AbstractEventLoop] = None

		self.Osu:PhaazebotOsu = PhaazebotOsu(self)
		self.OsuLoop:Optional[asyncio.AbstractEventLoop] = None

		self.Twitter = None
		self.TwitterLoop:Optional[asyncio.AbstractEventLoop] = None

		self.Web:PhaazebotWeb = PhaazebotWeb(self)
		self.WebLoop:Optional[asyncio.AbstractEventLoop] = None

		self.WorkerLoop:Optional[asyncio.AbstractEventLoop] = None # Worker object is protected and only gives us the loop in inject

		# this runs everything
		self.Mainframe:MainframeThread = MainframeThread(self)

		# this keeps track of what is running
		self.IsReady:IsReadyStore = IsReadyStore()

		# connection to phaaze brain
		self.PhaazeDB:DBConn = DBConn(
			host=self.Access.phaazedb_host,
			port=self.Access.phaazedb_port,
			user=self.Access.phaazedb_user,
			passwd=self.Access.phaazedb_password,
			database=self.Access.phaazedb_database
		)

	def start(self) -> None:
		self.Logger.info("Phaazebot Mainframe started -> Starting Threads...")
		initStartupTasks(self)
		self.Mainframe.start()


if __name__ == '__main__':
	Phaaze:Phaazebot = Phaazebot()
	GlobalStorage.add("Phaazebot", Phaaze)

	if CliArgs.get("log-sql", False):
		Phaaze.PhaazeDB.statement_func = Phaaze.Logger.printSQL

	if not CliArgs.get("no-start"):
		Phaaze.start()
