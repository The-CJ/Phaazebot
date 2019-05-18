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

class VarsStore(object):
	"""
		filled with permanent vars, or functions to get vars
	"""
	def __init__(self, config:ConfigParser):
		self.TRIGGER_DISCORD:str = config.get('trigger_discord', '>')
		self.TRIGGER_OSU:str = config.get('trigger_osu', '!')
		self.TRIGGER_TWITCH:str = config.get('trigger_twitch', '!')

		self.DEFAULT_TWITCH_CURRENCY:str = config.get('default_twitch_currency', 'Credit')
		self.DEFAULT_TWITCH_CURRENCY_MULTI:str = config.get('default_twitch_currency_multi', 'Credits')

		self.IMAGE_PATH:str = config.get('image_path', '_WEB_/img/')

		self.LOGO_OSU:str = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Osu%21Logo_%282015%29.png/600px-Osu%21Logo_%282015%29.png"
		self.LOGO_TWITCH:str = "https://i.redditmedia.com/za3YAsq33WcZc66FVb1cBw6mY5EibKpD_5hfLz0AbaE.jpg?w=320&s=53cf0ff252d84c5bb460b6ec0b195504" #TODO: remove this

	@property
	def LOGO(self):
		return "TODO: return logo"
