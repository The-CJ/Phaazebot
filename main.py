import time
from Utils.config import ConfigParser

class Phaazebot(object):
	"""docstring for """
	def __init__(self, config:ConfigParser=ConfigParser()):
		self.config:ConfigParser = config
		self.version:str = self.config.get("version", "[N/A]")
		self.start_time:int = time.time() # together with another time.time(), used to know how long phaaze is running

		#all featured "superclasses" aka, stuff that makes calls to somewhere
		self.discord = None
		self.twitch = None
		self.osu = None
		self.twitter = None





if __name__ == '__main__':
	Phaazebot = Phaazebot()
	print(vars(Phaazebot))
