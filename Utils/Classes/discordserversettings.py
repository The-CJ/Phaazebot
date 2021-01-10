from typing import List
from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.contentclass import ContentClass

class DiscordServerSettings(ContentClass):
	"""
	Contains and represents all possible discord server settings
	"""
	def __init__(self, data:dict):

		self.__found = False
		if data:
			self.__found = True

		# key
		self.guild_id:str = self.asString(data.get("guild_id", UNDEFINED))

		# vars
		self.autorole_id:str = self.asString(data.get("autorole_id", UNDEFINED))
		self.blacklist_ban_links:bool = self.asBoolean(data.get("blacklist_ban_links", UNDEFINED))
		self.blacklist_punishment:str = self.asString(data.get("blacklist_punishment", UNDEFINED))
		self.currency_name:str = self.asString(data.get("currency_name", UNDEFINED))
		self.currency_name_multi:str = self.asString(data.get("currency_name_multi", UNDEFINED))
		self.leave_chan:str = self.asString(data.get("leave_chan", UNDEFINED))
		self.leave_msg:str = self.asString(data.get("leave_msg", UNDEFINED))
		self.level_announce_chan:str = self.asString(data.get("level_announce_chan", UNDEFINED))
		self.level_custom_msg:str = self.asString(data.get("level_custom_msg", UNDEFINED))
		self.owner_disable_level:bool = self.asBoolean(data.get("owner_disable_level", UNDEFINED))
		self.owner_disable_normal:bool = self.asBoolean(data.get("owner_disable_normal", UNDEFINED))
		self.owner_disable_regular:bool = self.asBoolean(data.get("owner_disable_regular", UNDEFINED))
		self.owner_disable_mod:bool = self.asBoolean(data.get("owner_disable_mod", UNDEFINED))
		self.track_channel:str = self.asString(data.get("track_channel", UNDEFINED))
		self.track_value:int = self.asInteger(data.get("track_value", UNDEFINED))
		self.welcome_chan:str = self.asString(data.get("welcome_chan", UNDEFINED))
		self.welcome_msg:str = self.asString(data.get("welcome_msg", UNDEFINED))
		self.welcome_msg_priv:str = self.asString(data.get("welcome_msg_priv", UNDEFINED))

		# calc
		self.blacklist_whitelistroles:List[str] = self.fromStringList(data.get("blacklist_whitelistroles", UNDEFINED), separator=',')
		self.blacklist_whitelistlinks:List[str] = self.fromStringList(data.get("blacklist_whitelistlinks", UNDEFINED), separator=";;;")
		self.blacklist_blacklistwords:List[str] = self.fromStringList(data.get("blacklist_blacklistwords", UNDEFINED), separator=";;;")
		self.disabled_levelchannels:List[str] = self.fromStringList(data.get("disabled_levelchannels", UNDEFINED), separator=',')
		self.disabled_quotechannels:List[str] = self.fromStringList(data.get("disabled_quotechannels", UNDEFINED), separator=',')
		self.disabled_normalchannels:List[str] = self.fromStringList(data.get("disabled_normalchannels", UNDEFINED), separator=',')
		self.disabled_regularchannels:List[str] = self.fromStringList(data.get("disabled_regularchannels", UNDEFINED), separator=',')
		self.enabled_gamechannels:List[str] = self.fromStringList(data.get("enabled_gamechannels", UNDEFINED), separator=',')
		self.enabled_nsfwchannels:List[str] = self.fromStringList(data.get("enabled_nsfwchannels", UNDEFINED),separator=',')

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

		j["autorole_id"] = self.asString(self.autorole_id)
		j["blacklist_ban_links"] = self.asBoolean(self.blacklist_ban_links)
		j["blacklist_blacklistwords"] = self.asList(self.blacklist_blacklistwords)
		j["blacklist_punishment"] = self.asString(self.blacklist_punishment)
		j["blacklist_whitelistlinks"] = self.asList(self.blacklist_whitelistlinks)
		j["blacklist_whitelistroles"] = self.asList(self.blacklist_whitelistroles)
		j["currency_name"] = self.asString(self.currency_name)
		j["currency_name_multi"] = self.asString(self.currency_name_multi)
		j["disabled_levelchannels"] = self.asList(self.disabled_levelchannels)
		j["disabled_normalchannels"] = self.asList(self.disabled_normalchannels)
		j["disabled_quotechannels"] = self.asList(self.disabled_quotechannels)
		j["disabled_regularchannels"] = self.asList(self.disabled_regularchannels)
		j["enabled_gamechannels"] = self.asList(self.enabled_gamechannels)
		j["enabled_nsfwchannels"] = self.asList(self.enabled_nsfwchannels)
		j["leave_chan"] = self.asString(self.leave_chan)
		j["leave_msg"] = self.asString(self.leave_msg)
		j["level_announce_chan"] = self.asString(self.level_announce_chan)
		j["level_custom_msg"] = self.asString(self.level_custom_msg)
		j["owner_disable_level"] = self.asBoolean(self.owner_disable_level)
		j["owner_disable_mod"] = self.asBoolean(self.owner_disable_mod)
		j["owner_disable_normal"] = self.asBoolean(self.owner_disable_normal)
		j["owner_disable_regular"] = self.asBoolean(self.owner_disable_regular)
		j["track_channel"] = self.asString(self.track_channel)
		j["track_value"] = self.asInteger(self.track_value)
		j["welcome_chan"] = self.asString(self.welcome_chan)
		j["welcome_msg"] = self.asString(self.welcome_msg)
		j["welcome_msg_priv"] = self.asString(self.welcome_msg_priv)

		return j

	@property
	def server_id(self) -> str:
		return self.guild_id
