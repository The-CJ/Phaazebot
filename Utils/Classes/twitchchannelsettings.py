from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.dbcontentclass import DBContentClass
from Utils.Classes.apiclass import APIClass

class TwitchChannelSettings(DBContentClass, APIClass):
	"""
	Contains and represents all possible twitch channel settings
	"""
	def __init__(self, infos:dict = {}):

		self.__found = False
		if infos:
			self.__found = True

		# key
		self.channel_id:str = infos.get("channel_id", UNDEFINED)

		# vars
		self.active_game:bool = bool( infos.get("active_game", UNDEFINED) )
		self.active_level:bool = bool( infos.get("active_level", UNDEFINED) )
		self.active_quote:bool = bool( infos.get("active_quote", UNDEFINED) )
		self.blacklist_ban_links:bool = bool( infos.get("blacklist_ban_links", UNDEFINED) )
		self.blacklist_link_msg:str = infos.get("blacklist_link_msg", UNDEFINED)
		self.blacklist_msg:str = infos.get("blacklist_msg", UNDEFINED)
		self.blacklist_notify:bool = bool( infos.get("blacklist_notify", UNDEFINED) )
		self.blacklist_punishment:str = infos.get("blacklist_punishment", UNDEFINED)
		self.currency_name:str = infos.get("currency_name", UNDEFINED)
		self.currency_name_multi:str = infos.get("currency_name_multi", UNDEFINED)
		self.gain_currency:int = infos.get("gain_currency", UNDEFINED)
		self.gain_currency_active_multi:float = infos.get("gain_currency_active_multi", UNDEFINED)
		self.gain_currency_message:int = infos.get("gain_currency_message", UNDEFINED)
		self.osurequestformat_osu:str = infos.get("osurequestformat_osu", UNDEFINED)
		self.osurequestformat_twtich:str = infos.get("osurequestformat_twtich", UNDEFINED)
		self.owner_disable_level:bool = bool( infos.get("owner_disable_level", UNDEFINED) )
		self.owner_disable_mod:bool = bool( infos.get("owner_disable_mod", UNDEFINED) )
		self.owner_disable_normal:bool = bool( infos.get("owner_disable_normal", UNDEFINED) )
		self.owner_disable_regular:bool = bool( infos.get("owner_disable_regular", UNDEFINED) )

	def __bool__(self):
		return self.__found

	def __repr__(self):
		if self.__found:
			return f"<{self.__class__.__name__} channel_id='{self.channel_id}'>"
		else:
			return f"<{self.__class__.__name__} Empty configs>"

	def toJSON(self) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["autorole_id"] = self.toString(self.autorole_id)
		j["blacklist_ban_links"] = self.toBoolean(self.blacklist_ban_links)
		j["blacklist_blacklistwords"] = self.toList(self.blacklist_blacklistwords)
		j["blacklist_punishment"] = self.toString(self.blacklist_punishment)
		j["blacklist_whitelistlinks"] = self.toList(self.blacklist_whitelistlinks)
		j["blacklist_whitelistroles"] = self.toList(self.blacklist_whitelistroles)
		j["currency_name"] = self.toString(self.currency_name)
		j["currency_name_multi"] = self.toString(self.currency_name_multi)
		j["disabled_levelchannels"] = self.toList(self.disabled_levelchannels)
		j["disabled_normalchannels"] = self.toList(self.disabled_normalchannels)
		j["disabled_quotechannels"] = self.toList(self.disabled_quotechannels)
		j["disabled_regularchannels"] = self.toList(self.disabled_regularchannels)
		j["enabled_gamechannels"] = self.toList(self.enabled_gamechannels)
		j["enabled_nsfwchannels"] = self.toList(self.enabled_nsfwchannels)
		j["leave_chan"] = self.toString(self.leave_chan)
		j["leave_msg"] = self.toString(self.leave_msg)
		j["level_announce_chan"] = self.toString(self.level_announce_chan)
		j["level_custom_msg"] = self.toString(self.level_custom_msg)
		j["owner_disable_level"] = self.toBoolean(self.owner_disable_level)
		j["owner_disable_mod"] = self.toBoolean(self.owner_disable_mod)
		j["owner_disable_normal"] = self.toBoolean(self.owner_disable_normal)
		j["owner_disable_regular"] = self.toBoolean(self.owner_disable_regular)
		j["track_channel"] = self.toString(self.track_channel)
		j["track_value"] = self.toInteger(self.track_value)
		j["welcome_chan"] = self.toString(self.welcome_chan)
		j["welcome_msg"] = self.toString(self.welcome_msg)
		j["welcome_msg_priv"] = self.toString(self.welcome_msg_priv)

		return j
