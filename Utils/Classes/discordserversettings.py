from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.dbcontentclass import DBContentClass

class DiscordServerSettings(DBContentClass):
	"""
		Contains and represents all possible discord server settings
	"""
	def __init__(self, infos:dict = {}):

		self.__found = False
		if infos:
			self.__found = True

		self.autorole_id:str = infos.get("autorole_id", UNDEFINED)
		self.blacklist_ban_links:bool = bool( infos.get("blacklist_ban_links", UNDEFINED) )
		self.blacklist_whitelistroles:list = self.fromStringList( infos.get("blacklist_whitelistroles", UNDEFINED) )
		self.blacklist_whitelistlinks:list = self.fromStringList( infos.get("blacklist_whitelistlinks", UNDEFINED), ";;;" )
		self.blacklist_blacklistwords:list = self.fromStringList( infos.get("blacklist_blacklistwords", UNDEFINED), ";;;" )
		self.blacklist_punishment:str = infos.get("blacklist_punishment", UNDEFINED)
		self.currency_name:str = infos.get("currency_name", UNDEFINED)
		self.currency_name_multi:str = infos.get("currency_name_multi", UNDEFINED)
		self.disabled_levelchannels:list = self.fromStringList( infos.get("disabled_levelchannels", UNDEFINED) )
		self.disabled_quotechannels:list = self.fromStringList( infos.get("disabled_quotechannels", UNDEFINED) )
		self.disabled_normalchannels:list = self.fromStringList( infos.get("disabled_normalchannels", UNDEFINED) )
		self.disabled_regularchannels:list = self.fromStringList( infos.get("disabled_regularchannels", UNDEFINED) )
		self.enabled_gamechannels:list = self.fromStringList( infos.get("enabled_gamechannels", UNDEFINED) )
		self.enabled_nsfwchannels:list = self.fromStringList( infos.get("enabled_nsfwchannels", UNDEFINED) )
		self.leave_chan:str = infos.get("leave_chan", UNDEFINED)
		self.leave_msg:str = infos.get("leave_msg", UNDEFINED)
		self.level_announce_chan:str = infos.get("level_announce_chan", UNDEFINED)
		self.level_custom_msg:str = infos.get("level_custom_msg", UNDEFINED)
		self.owner_disable_level:bool = bool( infos.get("owner_disable_level", UNDEFINED) )
		self.owner_disable_normal:bool = bool( infos.get("owner_disable_normal", UNDEFINED) )
		self.owner_disable_regular:bool = bool( infos.get("owner_disable_regular", UNDEFINED) )
		self.owner_disable_mod:bool = bool( infos.get("owner_disable_mod", UNDEFINED) )
		self.server_id:str = infos.get("guild_id", UNDEFINED)
		self.track_channel:str = infos.get("track_channel", UNDEFINED)
		self.track_options:list = self.fromJsonField( infos.get("track_options", UNDEFINED) )
		self.welcome_chan:str = infos.get("welcome_chan", UNDEFINED)
		self.welcome_msg:str = infos.get("welcome_msg", UNDEFINED)
		self.welcome_msg_priv:str = infos.get("welcome_msg_priv", UNDEFINED)

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

		j["autorole_id"] = str(self.autorole_id)
		j["blacklist_ban_links"] = bool(self.blacklist_ban_links)
		j["blacklist_whitelistroles"] = list(self.blacklist_whitelistroles)
		j["blacklist_whitelistlinks"] = list(self.blacklist_whitelistlinks)
		j["blacklist_blacklistwords"] = list(self.blacklist_blacklistwords)
		j["blacklist_punishment"] = str(self.blacklist_punishment)
		j["currency_name"] = str(self.currency_name)
		j["currency_name_multi"] = str(self.currency_name_multi)
		j["disabled_levelchannels"] = list(self.disabled_levelchannels)
		j["disabled_quotechannels"] = list(self.disabled_quotechannels)
		j["disabled_normalchannels"] = list(self.disabled_normalchannels)
		j["disabled_regularchannels"] = list(self.disabled_regularchannels)
		j["enabled_gamechannels"] = list(self.enabled_gamechannels)
		j["enabled_nsfwchannels"] = list(self.enabled_nsfwchannels)
		j["level_announce_chan"] = str(self.level_announce_chan)
		j["level_custom_msg"] = str(self.level_custom_msg)
		j["leave_msg"] = str(self.leave_msg)
		j["leave_chan"] = str(self.leave_chan)
		j["owner_disable_level"] = bool(self.owner_disable_level)
		j["owner_disable_normal"] = bool(self.owner_disable_normal)
		j["owner_disable_regular"] = bool(self.owner_disable_regular)
		j["owner_disable_mod"] = bool(self.owner_disable_mod)
		j["track_channel"] = str(self.track_channel)
		j["track_options"] = list(self.track_options)
		j["welcome_chan"] = str(self.welcome_chan)
		j["welcome_msg"] = str(self.welcome_msg)
		j["welcome_msg_priv"] = str(self.welcome_msg_priv)

		return j
