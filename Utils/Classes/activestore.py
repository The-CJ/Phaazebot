from Utils.config import ConfigParser

class ActiveStore(object):
	"""
		used to keep track of all modules, if they should run or not
		gets configs from config file and provides alternative default
	"""
	def __init__(self, config:ConfigParser):
		# if this is not True, the program shuts down immediately
		self.main = bool(config.get('main', True))

		self.api:bool = bool(config.get('api', False))
		self.web:bool = bool(config.get('web', False))
		self.discord:bool = bool(config.get('discord', False))
		self.twitch_irc:bool = bool(config.get('twitch_irc', False))
		self.twitch_alert:bool = bool(config.get('twitch_alert', False))
		self.twitch_stream:bool = bool(config.get('twitch_stream', False))
		self.osu_irc:bool = bool(config.get('osu_irc', False))
		self.twitter:bool = bool(config.get('twitter', False))
		self.youtube:bool = bool(config.get('youtube', False))
