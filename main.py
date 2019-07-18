import asyncio
import time
import PhaazeDBC
from Utils.Classes.storeclasses import ActiveStore, VarsStore, AccessStore, LimitStore, IsReadyStore, GlobalStorage
from Utils.config import ConfigParser
from Utils.logger import PhaazeLogger
from Utils.threads import Mainframe

# platforms
from Platforms.Discord.main_discord import PhaazebotDiscord
from Platforms.Web.main_web import PhaazebotWeb

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
		# both the actual working part anda quick link to there running loops, to inject async funtions for them to run
		# most likly used for the worker, that can calculate time consuming functions or discord because send_message must be caled from this loop
		self.Discord:PhaazebotDiscord = None
		self.DiscordLoop:asyncio.AbstractEventLoop = None

		self.Twitch = None
		self.TwitchLoop:asyncio.AbstractEventLoop = None

		self.Osu = None
		self.OsuLoop:asyncio.AbstractEventLoop = None

		self.Twitter = None
		self.TwitterLoop:asyncio.AbstractEventLoop = None

		self.Web:PhaazebotWeb = None
		self.WebLoop:asyncio.AbstractEventLoop = None

		self.WorkerLoop:asyncio.AbstractEventLoop = None # Worker object is protected and only gives us the loop in inject

		# connection to phaaze brain
		self.PhaazeDB:PhaazeDBC.Connection = PhaazeDBC.Connection(
			address=self.Access.PHAAZEDB_ADDRESS,
			port=self.Access.PHAAZEDB_PORT,
			token=self.Access.PHAAZEDB_TOKEN,
			exception_on_error=True
		)

		# this runs everthing
		self.Mainframe = Mainframe(self)

		self.IsReady:IsReadyStore = IsReadyStore()

	def start(self) -> None:
		self.Logger.info("Phaazebot Mainframe started -> Starting Threads...")
		self.Mainframe.start()

if __name__ == '__main__':
	Phaaze = Phaazebot()
	GlobalStorage.add("Phaazebot", Phaaze)
	Phaaze.start()
