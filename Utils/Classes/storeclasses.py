from typing import TYPE_CHECKING, Any, Optional
if TYPE_CHECKING:
	from phaazebot import Phaazebot

import Platforms.Twitch.const as TwitchConst
import Platforms.Discord.const as DiscordConst
from Utils.Classes.undefined import UNDEFINED, Undefined
from Utils.cli import CliArgs

class StoreStructure(object):
	"""
	Simple class with some utility functions
	"""
	def __init__(self, BASE:"Phaazebot"):
		self.Phaaze:"Phaazebot" = BASE
		if not self.Phaaze.Config:
			raise AttributeError("Missing or unloaded ConfigParser in main Phaaze object")

	def load(self) -> None:
		"""
		This func. must be overwritten
		"""
		raise AttributeError("load() must be overwritten by Sub-Classes")

	def getFromConfig(self, a:str, b:Any, required:bool) -> Any:
		"""
		get `a` from configs else, return `b`
		if `required` and `a` was not found: -> panic
		"""
		value:Any = self.Phaaze.Config.get(a, UNDEFINED)
		if type(value) is Undefined:

			if required:
				errmsg:str = f"(Config) could not find '{a}' - but is marked as required"
				self.Phaaze.Logger.error(errmsg)
				raise AttributeError(errmsg)

			war_msg:str = f"(Config) can't find '{a}' - alternative '{str(b)}' is taken"
			self.Phaaze.Logger.debug(war_msg, require="config")
			return b

		else:
			if CliArgs.get("show-configs", ''):
				suc_msg:str = f"(Config) found '{a}' = '{str(value)}'"
				self.Phaaze.Logger.debug(suc_msg, require="config")

			return value

	def getBoolFromConfig(self, a:str, b:Optional[bool]=UNDEFINED, required:bool=False) -> bool:
		"""
		get value from configs as a bool
		"""
		value:Any = self.getFromConfig(a, b, required)
		return bool(value)

	def getStrFromConfig(self, a:str, b:Optional[str]=UNDEFINED, required:bool=False) -> str:
		"""
		get value from configs as a str
		"""
		value:Any = self.getFromConfig(a, b, required)
		return str(value)

	def getIntFromConfig(self, a:str, b:Optional[int]=UNDEFINED, required:bool=False) -> int:
		"""
		get value from configs as a int
		"""
		value:Any = self.getFromConfig(a, b, required)

		try:
			return int(value)
		except:
			return 0

class AccessStore(StoreStructure):
	"""
	Settings and Keys to all platforms or entry points that is not us
	"""

	def __init__(self, BASE: "Phaazebot"):
		super().__init__(BASE)

		# twitch
		self.twitch_irc_token:str = self.getStrFromConfig("twitch_irc_token")
		self.twitch_irc_nickname:str = self.getStrFromConfig("twitch_irc_nickname")
		self.twitch_client_secret:str = self.getStrFromConfig("twitch_client_secret")
		self.twitch_client_id:str = self.getStrFromConfig("twitch_client_id")
		self.twitch_client_credential_token:str = self.getStrFromConfig("twitch_client_credential_token")

		# discord
		self.discord_secret:str = self.getStrFromConfig("discord_secret")
		self.discord_token:str = self.getStrFromConfig("discord_token")

		# discord
		self.discord_secret:str = self.getStrFromConfig("discord_secret")
		self.discord_token:str = self.getStrFromConfig("discord_token")

		# osu
		self.osu_api_token:str = self.getStrFromConfig("osu_api_token")
		self.osu_irc_nickname:str = self.getStrFromConfig("osu_irc_nickname")
		self.osu_irc_token:str = self.getStrFromConfig("osu_irc_token")

		# other
		self.cleverbot_token:str = self.getStrFromConfig("cleverbot_token")
		self.mashape_token:str = self.getStrFromConfig("mashape_token")

		# database
		self.phaazedb_database:str = self.getStrFromConfig("phaazedb_database", "phaaze")
		self.phaazedb_host:str = self.getStrFromConfig("phaazedb_host", "localhost")
		self.phaazedb_password:str = self.getStrFromConfig("phaazedb_password", "")
		self.phaazedb_port:int = self.getIntFromConfig("phaazedb_port", 3306)
		self.phaazedb_user:str = self.getStrFromConfig("phaazedb_user", "phaaze")

		# twitter
		self.twitter_consumer_key:str = self.getStrFromConfig("twitter_consumer_key")
		self.twitter_consumer_secret:str = self.getStrFromConfig("twitter_consumer_secret")
		self.twitter_token_key:str = self.getStrFromConfig("twitter_token_key")
		self.twitter_token:str = self.getStrFromConfig("twitter_token")

class ActiveStore(StoreStructure):
	"""
	used to keep track of all modules, if they should run or not
	gets configs from config file and provides alternative default
	"""

	def __init__(self, BASE: "Phaazebot"):
		super().__init__(BASE)

		# if this is not True, the program shuts down immediately
		self.main:bool = self.getBoolFromConfig("active_main", True, required=True)

		self.api:bool = self.getBoolFromConfig("active_api", False, required=True)
		self.web:bool = self.getBoolFromConfig("active_web", False, required=True)
		self.discord:bool = self.getBoolFromConfig("active_discord", False, required=True)
		self.twitch_irc:bool = self.getBoolFromConfig("active_twitch_irc", False, required=True)
		self.twitch_events:bool = self.getBoolFromConfig("active_twitch_events", False, required=True)
		self.osu_irc:bool = self.getBoolFromConfig("active_osu_irc", False, required=True)
		self.twitter:bool = self.getBoolFromConfig("active_twitter", False, required=True)
		self.youtube:bool = self.getBoolFromConfig("active_youtube", False, required=True)

class LimitStore(StoreStructure):
	"""
	contains user limits for all addable things, like command amount and so on
	gets configs from config file and provides alternative default
	"""

	def __init__(self, BASE: "Phaazebot"):
		super().__init__(BASE)

		# amount's
		self.discord_assignrole_amount:int = self.getIntFromConfig("discord_assignrole_amount", DiscordConst.ASSIGNROLE_AMOUNT)
		self.discord_commands_amount:int = self.getIntFromConfig("discord_commands_amount", DiscordConst.COMMAND_AMOUNT)
		self.discord_level_medal_amount:int = self.getIntFromConfig("discord_level_medal_amount", DiscordConst.LEVEL_MEDAL_AMOUNT)
		self.discord_quotes_amount:int = self.getIntFromConfig("discord_quotes_amount", DiscordConst.QUOTE_AMOUNT)
		self.discord_regular_amount:int = self.getIntFromConfig("discord_regular_amount", DiscordConst.REGULAR_AMOUNT)
		self.twitch_custom_command_amount:int = self.getIntFromConfig("twitch_custom_command_amount", TwitchConst.COMMAND_AMOUNT)
		self.twitch_quote_amount:int = self.getIntFromConfig("twitch_quote_amount", TwitchConst.QUOTE_AMOUNT)

		# cooldown's
		self.discord_commands_cooldown_max:int = self.getIntFromConfig("discord_commands_cooldown_max", DiscordConst.COMMAND_COOLDOWN_MAX)
		self.discord_commands_cooldown_min:int = self.getIntFromConfig("discord_commands_cooldown_min", DiscordConst.COMMAND_COOLDOWN_MIN)
		self.twitch_commands_cooldown_max:int = self.getIntFromConfig("twitch_commands_cooldown_max", TwitchConst.COMMAND_COOLDOWN_MAX)
		self.twitch_commands_cooldown_min:int = self.getIntFromConfig("twitch_commands_cooldown_min", TwitchConst.COMMAND_COOLDOWN_MIN)
		self.discord_level_cooldown:int = self.getIntFromConfig("discord_level_cooldown", TwitchConst.LEVEL_COOLDOWN)
		self.twitch_punish_time_max:int = self.getIntFromConfig("twitch_punish_time_max", TwitchConst.PUNISH_TIME_MAX)
		self.twitch_punish_time_min:int = self.getIntFromConfig("twitch_punish_time_min", TwitchConst.PUNISH_TIME_MIN)

		# other's
		self.web_client_max_size:int = self.getIntFromConfig("web_client_max_size", 5242880) # 5MB

class VarsStore(StoreStructure):
	"""
	filled with permanent vars/const, or functions to get values
	"""

	def __init__(self, BASE: "Phaazebot"):
		super().__init__(BASE)

		# debug
		self.discord_debug_user_id:list = list(self.getFromConfig("discord_debug_user_id", [], False))
		self.twitch_debug_user_id:list = list(self.getFromConfig("twitch_debug_user_id", [], False))

		# IDs
		self.discord_bot_id:str = self.getStrFromConfig("discord_bot_id", "")
		self.twitch_bot_id:str = self.getStrFromConfig("twitch_bot_id", "")

		# currency names
		self.default_discord_currency_multi:str = self.getStrFromConfig("default_discord_currency_multi", "Credits")
		self.default_discord_currency:str = self.getStrFromConfig("default_discord_currency", "Credits")
		self.default_twitch_currency_multi:str = self.getStrFromConfig("default_twitch_currency_multi", "Credits")
		self.default_twitch_currency:str = self.getStrFromConfig("default_twitch_currency", "Credit")

		# (redirect) links
		self.discord_redirect_link:str = self.getStrFromConfig("discord_redirect_link", "localhost", required=True)
		self.twitch_redirect_link:str = self.getStrFromConfig("twitch_redirect_link", "localhost", required=True)

		# other
		self.discord_modt:str = self.getStrFromConfig("discord_motd", "Hello there")

		# web stuff
		self.web_root:str = self.getStrFromConfig("web_root", "localhost")
		self.ssl_dir:str = self.getStrFromConfig("ssl_dir", "/etc/letsencrypt/live/domain.something/")

		# Logos
		self.logo_osu:str = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Osu%21Logo_%282015%29.png/600px-Osu%21Logo_%282015%29.png"
		self.logo_twitch:str = "https://i.redditmedia.com/za3YAsq33WcZc66FVb1cBw6mY5EibKpD_5hfLz0AbaE.jpg?w=320&s=53cf0ff252d84c5bb460b6ec0b195504"

class IsReadyStore(object):
	"""
	Contains the state if something is ready or not
	all start False, turn True when connected
	"""
	def __init__(self):
		self.discord:bool = False
		self.osu:bool = False
		self.twitch:bool = False
		self.twitter:bool = False
		self.web:bool = False
		self.youtube:bool = False

class GlobalStorageClass(object):
	"""
	This Class is strange.
	It suppose to be accessed from other modules via:

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


GlobalStorage:GlobalStorageClass = GlobalStorageClass()
