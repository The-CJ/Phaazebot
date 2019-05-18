import time
import PhaazeDBC
from Utils.Classes.storeclasses import ActiveStore, VarsStore
from Utils.config import ConfigParser

# platforms
from Platforms.Discord.main_discord import PhaazebotDiscord

class Phaazebot(object):
	"""docstring for """
	def __init__(self, config:ConfigParser=ConfigParser()):
		self.config:ConfigParser = config
		self.version:str = self.config.get("version", "[N/A]")
		self.start_time:int = time.time() # together with another time.time(), used to know how long phaaze is running

		# get the active/load class, aka, what sould get started
		self.active:ActiveStore = ActiveStore(self.config)

		# a class filled with permanent vars, mainly from external sources or whatever
		self.vars:VarsStore = VarsStore(self.config)

		# all featured "superclasses" aka, stuff that makes calls to somewhere
		self.discord:PhaazebotDiscord = None
		self.twitch = None
		self.osu = None
		self.twitter = None

		#self.PhaazeDB = PhaazeDBC.Connection(port=3000, token=self.config.PhaazeDB_token, exception_on_error=True)



if __name__ == '__main__':
	Phaazebot = Phaazebot()
	print(vars(Phaazebot))
