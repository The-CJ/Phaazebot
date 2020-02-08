from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.dbcontentclass import DBContentClass
from Utils.Classes.apiclass import APIClass

class DiscordServerSettings(DBContentClass, APIClass):
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

		j["autorole_id"] = self.toString(self.autorole_id)
		j["blacklist_ban_links"] = self.toBoolean(self.blacklist_ban_links)
		j["blacklist_whitelistroles"] = self.toList(self.blacklist_whitelistroles)
		j["blacklist_whitelistlinks"] = self.toList(self.blacklist_whitelistlinks)
		j["blacklist_blacklistwords"] = self.toList(self.blacklist_blacklistwords)
		j["blacklist_punishment"] = self.toString(self.blacklist_punishment)
		j["currency_name"] = self.toString(self.currency_name)
		j["currency_name_multi"] = self.toString(self.currency_name_multi)
		j["disabled_levelchannels"] = self.toList(self.disabled_levelchannels)
		j["disabled_quotechannels"] = self.toList(self.disabled_quotechannels)
		j["disabled_normalchannels"] = self.toList(self.disabled_normalchannels)
		j["disabled_regularchannels"] = self.toList(self.disabled_regularchannels)
		j["enabled_gamechannels"] = self.toList(self.enabled_gamechannels)
		j["enabled_nsfwchannels"] = self.toList(self.enabled_nsfwchannels)
		j["level_announce_chan"] = self.toString(self.level_announce_chan)
		j["level_custom_msg"] = self.toString(self.level_custom_msg)
		j["leave_msg"] = self.toString(self.leave_msg)
		j["leave_chan"] = self.toString(self.leave_chan)
		j["owner_disable_level"] = self.toBoolean(self.owner_disable_level)
		j["owner_disable_normal"] = self.toBoolean(self.owner_disable_normal)
		j["owner_disable_regular"] = self.toBoolean(self.owner_disable_regular)
		j["owner_disable_mod"] = self.toBoolean(self.owner_disable_mod)
		j["track_channel"] = self.toString(self.track_channel)
		j["track_options"] = self.toList(self.track_options)
		j["welcome_chan"] = self.toString(self.welcome_chan)
		j["welcome_msg"] = self.toString(self.welcome_msg)
		j["welcome_msg_priv"] = self.toString(self.welcome_msg_priv)

		return j
