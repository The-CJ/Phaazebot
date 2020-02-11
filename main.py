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
from Utils.threads import Mainframe
from Utils.Classes.dbconn import DBConn
from Utils.cli import CliArgs

# platforms
from Platforms.Discord.main_discord import PhaazebotDiscord
from Platforms.Web.main_web import PhaazebotWeb
from Platforms.Osu.main_osu import PhaazebotOsu
from Platforms.Twitch.main_events import PhaazebotTwitchEvents

class Phaazebot(object):
	"""
		mainclass containing all other informations.
		thats phaaze
	"""
	def __init__(self, Config:ConfigParser=ConfigParser()):
		self.Config:ConfigParser = Config
		self.version:str = self.Config.get("version", "[N/A]")
		self.start_time:int = time.time() # together with another time.time(), used to know how long phaaze is running

		# get the active/load class, aka, what sould get started
		self.Active:ActiveStore = ActiveStore(self.Config)

		# a class filled with permanent vars, mainly from external sources or whatever
		self.Vars:VarsStore = VarsStore(self.Config)

		# the key to everything, that will be needed to connect to everything thats not ourself
		self.Access:AccessStore = AccessStore(self.Config)

		# contains user limits for all addeble things, like custom command amount
		self.Limit:LimitStore = LimitStore(self.Config)

		# log to handler of choice
		self.Logger:PhaazeLogger = PhaazeLogger()

		# all featured "superclasses" aka, stuff that makes calls to somewhere
		# all of these get added by self.Mainframe when started
		# both the actual working part and a quick link to there running loops, to inject async funtions for them to run
		# most likly used for the worker, that can calculate time consuming functions or discord because send_message must be called from this loop
		self.Discord:PhaazebotDiscord = PhaazebotDiscord(self)
		self.DiscordLoop:asyncio.AbstractEventLoop = None

		self.Twitch = None
		self.TwitchLoop:asyncio.AbstractEventLoop = None

		self.TwitchEvents:PhaazebotTwitchEvents = PhaazebotTwitchEvents(self)
		self.TwitchEventsLoop:asyncio.AbstractEventLoop = None

		self.Osu:PhaazebotOsu = PhaazebotOsu(self)
		self.OsuLoop:asyncio.AbstractEventLoop = None

		self.Twitter = None
		self.TwitterLoop:asyncio.AbstractEventLoop = None

		self.Web:PhaazebotWeb = PhaazebotWeb(self)
		self.WebLoop:asyncio.AbstractEventLoop = None

		self.WorkerLoop:asyncio.AbstractEventLoop = None # Worker object is protected and only gives us the loop in inject

		# this runs everthing
		self.Mainframe = Mainframe(self)

		# this keeps track of what is running
		self.IsReady:IsReadyStore = IsReadyStore()

		# connection to phaaze brain
		self.PhaazeDB:DBConn = DBConn(
			host = self.Access.PHAAZEDB_HOST,
			port = self.Access.PHAAZEDB_PORT,
			user = self.Access.PHAAZEDB_USER,
			passwd = self.Access.PHAAZEDB_PASSWORD,
			database = self.Access.PHAAZEDB_DATABASE
		)

	def start(self) -> None:
		self.Logger.info("Phaazebot Mainframe started -> Starting Threads...")
		self.Mainframe.start()

if __name__ == '__main__':
	Phaaze:Phaazebot = Phaazebot()
	GlobalStorage.add("Phaazebot", Phaaze)

	if CliArgs.get("log-sql", False):
		Phaaze.PhaazeDB.statement_func = Phaaze.Logger.printSQL

	Phaaze.start()
