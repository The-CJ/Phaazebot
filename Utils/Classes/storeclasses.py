from typing import Any
from Utils.config import ConfigParser
from Utils.Classes.undefined import UNDEFINED

class AccessStore(object):
	"""
	Settings and Keys to all platforms or entry points that is not us
	"""
	def __init__(self, config:ConfigParser):
		self.twitch_client_id:str = str(config.get("twitch_client_id", ''))
		self.twitch_client_secret:str = str(config.get("twitch_client_secret", ''))
		self.twitch_client_credential_token:str = "[N/A]"
		self.twitch_irc_token:str = str(config.get("twitch_irc_token", ''))

		self.discord_token:str = str(config.get("discord_token", ''))
		self.discord_secret:str = str(config.get("discord_secret", ''))

		self.osu_api_token:str = str(config.get("osu_api_token", ''))
		self.osu_irc_username:str = str(config.get("osu_irc_username", ''))
		self.osu_irc_token:str = str(config.get("osu_irc_token", ''))

		self.cleverbot_token:str = str(config.get("cleverbot_token", ''))

		self.mashape_token:str = str(config.get("mashape_token", ''))

		self.phaazedb_host:str = str(config.get("phaazedb_host", "localhost"))
		self.phaazedb_user:str = str(config.get("phaazedb_user", "phaaze"))
		self.phaazedb_password:str = str(config.get("phaazedb_password", ''))
		self.phaazedb_database:str = str(config.get("phaazedb_database", "phaaze"))
		self.phaazedb_port:str = str(config.get("phaazedb_port", "3306"))

		self.twitter_token:str = str(config.get("twitter_token",''))
		self.twitter_token_key:str = str(config.get("twitter_token_key",''))
		self.twitter_consumer_key:str = str(config.get("twitter_consumer_key",''))
		self.twitter_consumer_secret:str = str(config.get("twitter_consumer_secret",''))

class ActiveStore(object):
	"""
	used to keep track of all modules, if they should run or not
	gets configs from config file and provides alternative default
	"""
	def __init__(self, config:ConfigParser):
		# if this is not True, the program shuts down immediately
		self.main = bool(config.get("active_main", True))

		self.api:bool = bool(config.get("active_api", False))
		self.web:bool = bool(config.get("active_web", False))
		self.discord:bool = bool(config.get("active_discord", False))
		self.twitch_irc:bool = bool(config.get("active_twitch_irc", False))
		self.twitch_events:bool = bool(config.get("active_twitch_events", False))
		self.osu_irc:bool = bool(config.get("active_osu_irc", False))
		self.twitter:bool = bool(config.get("active_twitter", False))
		self.youtube:bool = bool(config.get("active_youtube", False))

class IsReadyStore(object):
	"""
	Containes the state if something is ready or not
	all start False, turn True when connected
	"""
	def __init__(self):
		self.web:bool = False
		self.discord:bool = False
		self.twitch:bool = False
		self.osu:bool = False
		self.twitter:bool = False
		self.youtube:bool = False

class LimitStore(object):
	"""
	contains user limits for all addeble things, like command amount and so on
	gets configs from config file and provides alternative default
	"""
	def __init__(self, config:ConfigParser):
		self.discord_commands_amount:int = int(config.get("discord_custom_commands_amount", 100))
		self.discord_commands_cooldown_min:int = int(config.get("discord_custom_commands_cooldown_min", 3))
		self.discord_commands_cooldown_max:int = int(config.get("discord_custom_commands_cooldown_max", 600))
		self.discord_level_cooldown:int = int(config.get("discord_level_cooldown", 3))
		self.discord_level_medal_amount:int = int(config.get("discord_level_medal_amount", 50))
		self.discord_quotes_amount:int = int(config.get("discord_quotes_amount", 100))
		self.discord_assignrole_amount:int = int(config.get("discord_assignrole_amount", 25))
		self.discord_regular_amount:int = int(config.get("discord_regular_amount", 50))

		self.twitch_timeout_message_cooldown:int = int(config.get("twitch_timeout_message_cooldown", 20))
		self.twitch_blacklist_remember_time:int = int(config.get("twitch_blacklist_remember_time", 180))
		self.twitch_custom_command_amount:int = int(config.get("twitch_custom_command_amount", 100))
		self.twitch_quote_amount:int = int(config.get("twitch_quote_amount", 100))
		self.twitch_stats_cooldown:int = int(config.get("twitch_stats_cooldown", 5))

		self.web_client_max_size:int = int(config.get("web_client_max_size", 5242880)) #5MB

class VarsStore(object):
	"""
	filled with permanent vars/const, or functions to get values
	"""
	def __init__(self, config:ConfigParser):
		self.discord_modt:str = str(config.get("discord_motd", "Hello there"))
		self.discord_debug_user_id:list = list(config.get("discord_debug_user_id", []))

		self.default_twitch_currency:str = str(config.get("default_twitch_currency", "Credit"))
		self.default_twitch_currency_multi:str = str(config.get("default_twitch_currency_multi", "Credits"))
		self.default_discord_currency:str = str(config.get("default_discord_currency", "Credit"))
		self.default_discord_currency_multi:str = str(config.get("default_discord_currency_multi", "Credits"))

		self.web_root:str = str(config.get("web_root", "localhost"))
		self.ssl_dir:str = str(config.get("ssl_dir", "/etc/letsencrypt/live/domain.something/"))

		self.discord_bot_id:str = str(config.get("discord_bot_id", "00000"))
		self.discord_login_link:str = str(config.get("discord_login_link", "/discord"))
		self.discord_redirect_link:str = str(config.get("discord_redirect_link", "localhost"))

		self.twitch_bot_id:str = str(config.get("twitch_bot_id", "00000"))
		self.twitch_login_link:str = str(config.get("twitch_login_link", "/twitch"))
		self.twitch_redirect_link:str = str(config.get("twitch_redirect_link", "localhost"))

		self.logo_osu:str = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Osu%21Logo_%282015%29.png/600px-Osu%21Logo_%282015%29.png"
		self.logo_twitch:str = "https://i.redditmedia.com/za3YAsq33WcZc66FVb1cBw6mY5EibKpD_5hfLz0AbaE.jpg?w=320&s=53cf0ff252d84c5bb460b6ec0b195504"

class GlobalStorage(object):
	"""
	This Class is strange.
	It suppost to be accessed from other modules via:

	from Utils.Classes.storeclasses import GlobalStorage

	It's something like a global dict.
	only has three functions: add, get, rem
	"""
	def __init__(self):
		self.__store:dict = dict()

	def add(self, key:str, value:Any) -> None:
		self.__store[key] = value

	def get(self, key:str, alt:Any=UNDEFINED) -> Any:
		return self.__store.get(key, alt)

	def rem(self, key:str, alt:Any=UNDEFINED) -> Any:
		return self.__store.pop(key, alt)

GlobalStorage = GlobalStorage()
