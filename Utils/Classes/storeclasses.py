from Utils.config import ConfigParser

class AccessStore(object):
	"""
		Settings and Keys to all platforms or entry points that is not us
	"""
	def __init__(self, config:ConfigParser):
		self.TWITCH_API_TOKEN:str = str(config.get('twitch_api_token', ''))
		self.TWITCH_IRC_TOKEN:str = str(config.get('twitch_irc_token', ''))
		self.TWITCH_ADMIN_TOKEN:str = str(config.get('twitch_admin_token', ''))

		self.DISCORD_TOKEN:str = str(config.get('discord_token', ''))
		self.DISCORD_SECRET:str = str(config.get('discord_secret', ''))

		self.OSU_API_TOKEN:str = str(config.get('osu_api_token', ''))
		self.OSU_IRC_TOKEN:str = str(config.get('osu_irc_token', ''))

		self.CLEVERBOT_TOKEN:str = str(config.get('cleverbot_token', ''))

		self.MASHAPE_TOKEN:str = str(config.get('mashape_token', ''))

		self.PHAAZEDB_ADDRESS:str = str(config.get('phaazedb_address', 'http://127.0.0.1'))
		self.PHAAZEDB_TOKEN:str = str(config.get('phaazedb_token', ''))
		self.PHAAZEDB_PORT:str = str(config.get('phaazedb_port', 3000))

		self.TWITTER_TOKEN:str = str(config.get('twitter_token',''))
		self.TWITTER_TOKEN_KEY:str = str(config.get('twitter_token_key',''))
		self.TWITTER_CONSUMER_KEY:str = str(config.get('twitter_consumer_key',''))
		self.TWITTER_CONSUMER_SECRET:str = str(config.get('twitter_consumer_secret',''))

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

class IsReadyStore(object):
	"""
		Containes the state if something s ready or not
		all start False, turn True when connected
	"""
	def __init__(self):
		self.discord = False
		self.twitch = False
		self.osu = False
		self.twitter = False
		self.youtube = False

class LimitStore(object):
	"""
		contains user limits for all addeble things, like custom command amount
		gets configs from config file and provides alternative default

	"""
	def __init__(self, config:ConfigParser):
		self.DISCORD_PRIVATE_COOLDOWN:int = int(config.get("discord_private_cooldown", 1))
		self.DISCORD_NORMAL_COOLDOWN:int = int(config.get("discord_normal_cooldown", 1))
		self.DISCORD_MOD_COOLDOWN:int = int(config.get("discord_mod_cooldown", 3))
		self.DISCORD_OWNER_COOLDOWN:int = int(config.get("discord_owner_cooldown", 5))
		self.DISCORD_CUSTOM_COMAMNDS_AMOUNT:int = int(config.get("discord_custom_commands_amount", 100))
		self.DISCORD_CUSTOM_COMMANDS_COOLDOWN:int = int(config.get("discord_custom_commands_cooldown", 3))
		self.DISCORD_LEVEL_COOLDOWN:int = int(config.get("discord_level_cooldown", 3))
		self.DISCORD_QUOTES_AMOUNT:int = int(config.get("discord_quotes_amount", 100))
		self.DISCORD_ADDROLE_AMOUNT:int = int(config.get("discord_addrole_amount", 25))

		self.TWITCH_TIMEOUT_MESSAGE_COOLDOWN:int = int(config.get("twitch_timeout_message_cooldown", 20))
		self.TWITCH_BLACKLIST_REMEMBER_TIME:int = int(config.get("twitch_blacklist_remember_time", 180))
		self.TWITCH_CUSTOM_COMMAND_AMOUNT:int = int(config.get("twitch_custom_command_amount", 100))
		self.TWITCH_QUOTE_AMOUNT:int = int(config.get("twitch_quote_amount", 100))
		self.TWITCH_STATS_COOLDOWN:int = int(config.get("twitch_stats_cooldown", 5))

		self.WEB_CLIENT_MAX_SIZE:int = int(config.get("web_client_max_size", 5242880)) #5MB

class VarsStore(object):
	"""
		filled with permanent vars, or functions to get vars
	"""
	def __init__(self, config:ConfigParser):
		self.TRIGGER_DISCORD:str = str(config.get('trigger_discord', '>'))
		self.TRIGGER_OSU:str = str(config.get('trigger_osu', '!'))
		self.TRIGGER_TWITCH:str = str(config.get('trigger_twitch', '!'))

		self.DEFAULT_TWITCH_CURRENCY:str = str(config.get('default_twitch_currency', 'Credit'))
		self.DEFAULT_TWITCH_CURRENCY_MULTI:str = str(config.get('default_twitch_currency_multi', 'Credits'))

		self.IMAGE_PATH:str = str(config.get('image_path', '_WEB_/img/'))

		self.DISCORD_LOGIN_LINK:str = str(config.get('discord_login_link', '/discord'))

		self.LOGO_OSU:str = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Osu%21Logo_%282015%29.png/600px-Osu%21Logo_%282015%29.png"
		self.LOGO_TWITCH:str = "https://i.redditmedia.com/za3YAsq33WcZc66FVb1cBw6mY5EibKpD_5hfLz0AbaE.jpg?w=320&s=53cf0ff252d84c5bb460b6ec0b195504"

	@property
	def LOGO(self):
		return "TODO: return logo"
