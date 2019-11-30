from Utils.Classes.undefined import Undefined
from Utils.Classes.dbcontentclass import DBContentClass

class DiscordServerSettings(DBContentClass):
	"""
		Contains and represents all possible discord server settings
	"""
	def __init__(self, infos:dict = {}):

		self.__found = False
		if infos:
			self.__found = True

		self.autorole_id:str = infos.get("autorole_id", Undefined())
		self.blacklist_ban_links:bool = bool( infos.get("blacklist_ban_links", Undefined()) )
		self.blacklist_whitelistroles:list = self.fromStringList( infos.get("blacklist_whitelistroles", Undefined()) )
		self.blacklist_whitelistlinks:list = self.fromStringList( infos.get("blacklist_whitelistlinks", Undefined()), ";;;" )
		self.blacklist_blacklistwords:list = self.fromStringList( infos.get("blacklist_blacklistwords", Undefined()), ";;;" )
		self.blacklist_punishment:str = infos.get("blacklist_punishment", Undefined())
		self.currency_name:str = infos.get("currency_name", Undefined())
		self.currency_name_multi:str = infos.get("currency_name_multi", Undefined())
		self.disabled_levelchannels:list = self.fromStringList( infos.get("disabled_levelchannels", Undefined()) )
		self.disabled_quotechannels:list = self.fromStringList( infos.get("disabled_quotechannels", Undefined()) )
		self.disabled_normalchannels:list = self.fromStringList( infos.get("disabled_normalchannels", Undefined()) )
		self.disabled_regularchannels:list = self.fromStringList( infos.get("disabled_regularchannels", Undefined()) )
		self.enabled_gamechannels:list = self.fromStringList( infos.get("enabled_gamechannels", Undefined()) )
		self.enabled_nsfwchannels:list = self.fromStringList( infos.get("enabled_nsfwchannels", Undefined()) )
		self.leave_chan:str = infos.get("leave_chan", Undefined())
		self.leave_msg:str = infos.get("leave_msg", Undefined())
		self.level_announce_chan:str = infos.get("level_announce_chan", Undefined())
		self.level_custom_msg:str = infos.get("level_custom_msg", Undefined())
		self.owner_disable_level:bool = bool( infos.get("owner_disable_level", Undefined()) )
		self.owner_disable_normal:bool = bool( infos.get("owner_disable_normal", Undefined()) )
		self.owner_disable_regular:bool = bool( infos.get("owner_disable_regular", Undefined()) )
		self.owner_disable_mod:bool = bool( infos.get("owner_disable_mod", Undefined()) )
		self.server_id:str = infos.get("guild_id", Undefined())
		self.track_channel:str = infos.get("track_channel", Undefined())
		self.track_options:list = self.fromJsonField( infos.get("track_options", Undefined()) )
		self.welcome_chan:str = infos.get("welcome_chan", Undefined())
		self.welcome_msg:str = infos.get("welcome_msg", Undefined())
		self.welcome_msg_priv:str = infos.get("welcome_msg_priv", Undefined())

	def __bool__(self):
		return self.__found

	def __repr__(self):
		if self.__found:
			return f"<{self.__class__.__name__} guild_id='{self.server_id}'>"
		else:
			return f"<{self.__class__.__name__} Empty configs>"

	def toJSON(self) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["autorole_id"] = self.autorole_id
		j["blacklist_ban_links"] = self.blacklist_ban_links
		j["blacklist_whitelistroles"] = self.blacklist_whitelistroles
		j["blacklist_whitelistlinks"] = self.blacklist_whitelistlinks
		j["blacklist_blacklistwords"] = self.blacklist_blacklistwords
		j["blacklist_punishment"] = self.blacklist_punishment
		j["currency_name"] = self.currency_name
		j["currency_name_multi"] = self.currency_name_multi
		j["disabled_levelchannels"] = self.disabled_levelchannels
		j["disabled_quotechannels"] = self.disabled_quotechannels
		j["disabled_normalchannels"] = self.disabled_normalchannels
		j["disabled_regularchannels"] = self.disabled_regularchannels
		j["enabled_gamechannels"] = self.enabled_gamechannels
		j["enabled_nsfwchannels"] = self.enabled_nsfwchannels
		j["level_announce_chan"] = self.level_announce_chan
		j["level_custom_msg"] = self.level_custom_msg
		j["leave_msg"] = self.leave_msg
		j["leave_chan"] = self.leave_chan
		j["owner_disable_level"] = self.owner_disable_level
		j["owner_disable_normal"] = self.owner_disable_normal
		j["owner_disable_regular"] = self.owner_disable_regular
		j["owner_disable_mod"] = self.owner_disable_mod
		j["track_channel"] = self.track_channel
		j["track_options"] = self.track_options
		j["welcome_chan"] = self.welcome_chan
		j["welcome_msg"] = self.welcome_msg
		j["welcome_msg_priv"] = self.welcome_msg_priv

		return j
