import asyncio
import time
import PhaazeDBC
from Utils.Classes.storeclasses import ActiveStore, VarsStore, AccessStore, LimitStore
from Utils.config import ConfigParser

# platforms
from Platforms.Discord.main_discord import PhaazebotDiscord

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

		# all featured "superclasses" aka, stuff that makes calls to somewhere
		self.Discord:PhaazebotDiscord = None
		self.Twitch = None
		self.Osu = None
		self.Twitter = None

		#self.Logger

		# connection to phaaze brain
		self.PhaazeDB:PhaazeDBC.Connection = PhaazeDBC.Connection(
			address=self.Access.phaazedb_address,
			port=self.Access.phaazedb_port,
			token=self.Access.phaazedb_token,
			exception_on_error=True
		)



if __name__ == '__main__':
	Phaazebot = Phaazebot()
