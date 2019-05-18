from Utils.config import ConfigParser

class AccessStore(object):
	"""
		Settings and Keys to all platforms or entry points that is not us
	"""
	def __init__(self, config:ConfigParser):
		self.twitch_api_token:str = config.get('twitch_api_token', '')
		self.twitch_irc_token:str = config.get('twitch_irc_token', '')
		self.twitch_admin_token:str = config.get('twitch_admin_token', '')

		self.discord_token = config.get('discord_token', '')

		self.osu_api_token = config.get('osu_api_token', '')
		self.osu_irc_token = config.get('osu_irc_token', '')

		self.cleverbot_token = config.get('cleverbot_token', '')

		self.mashape_token = config.get('mashape_token', '')

		self.phaazedb_token = config.get('phaazedb_token', '')

		self.twitter_token = config.get('twitter_token','')
		self.twitter_token_key = config.get('twitter_token_key','')
		self.twitter_consumer_key = config.get('twitter_consumer_key','')
		self.twitter_consumer_secret = config.get('twitter_consumer_secret','')

class ActiveStore(object):
	"""
		used to keep track of all modules, if they should run or not
		gets configs from config file and provides alternative default
	"""
	def __init__(self, config:ConfigParser):
		# if this is not True, the program shuts down immediately
		self.main = bool(config.get('active_main', True))

		self.api:bool = bool(config.get('active_api', False))
		self.web:bool = bool(config.get('active_web', False))
		self.discord:bool = bool(config.get('active_discord', False))
		self.twitch_irc:bool = bool(config.get('active_twitch_irc', False))
		self.twitch_alert:bool = bool(config.get('active_twitch_alert', False))
		self.twitch_stream:bool = bool(config.get('active_twitch_stream', False))
		self.osu_irc:bool = bool(config.get('active_osu_irc', False))
		self.twitter:bool = bool(config.get('active_twitter', False))
		self.youtube:bool = bool(config.get('active_youtube', False))

class VarsStore(object):
	"""
		filled with permanent vars, or functions to get vars
	"""
	def __init__(self, config:ConfigParser):
		self.trigger_discord:str = config.get('trigger_discord', '>')
		self.trigger_osu:str = config.get('trigger_osu', '!')
		self.trigger_twitch:str = config.get('trigger_twitch', '!')

		self.default_twitch_currency:str = config.get('default_twitch_currency', 'Credit')
		self.default_twitch_currency_multi:str = config.get('default_twitch_currency_multi', 'Credits')

		self.image_path:str = config.get('image_path', '_WEB_/img/')

		self.logo_osu:str = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Osu%21Logo_%282015%29.png/600px-Osu%21Logo_%282015%29.png"
		self.logo_twitch:str = "https://i.redditmedia.com/za3YAsq33WcZc66FVb1cBw6mY5EibKpD_5hfLz0AbaE.jpg?w=320&s=53cf0ff252d84c5bb460b6ec0b195504"

	@property
	def LOGO(self):
		return "TODO: return logo"
