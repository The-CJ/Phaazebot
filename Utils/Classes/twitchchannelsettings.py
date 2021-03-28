from typing import List
from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.contentclass import ContentClass

class TwitchChannelSettings(ContentClass):
	"""
	Contains and represents all possible twitch channel settings
	"""
	def __init__(self, data:dict):

		self.__found = False
		if data:
			self.__found = True

		# key
		self.channel_id:str = self.asString(data.get("channel_id", UNDEFINED))

		# vars
		self.active_game:bool = self.asBoolean(data.get("active_game", UNDEFINED))
		self.active_level:bool = self.asBoolean(data.get("active_level", UNDEFINED))
		self.active_quote:bool = self.asBoolean(data.get("active_quote", UNDEFINED))
		self.currency_name:str = self.asString(data.get("currency_name", UNDEFINED))
		self.currency_name_multi:str = self.asString(data.get("currency_name_multi", UNDEFINED))
		self.gain_currency:int = self.asInteger(data.get("gain_currency", UNDEFINED))
		self.gain_currency_active_multi:float = self.asFloat(data.get("gain_currency_active_multi", UNDEFINED))
		self.gain_currency_message:int = self.asInteger(data.get("gain_currency_message", UNDEFINED))
		self.osurequestformat_osu:str = self.asString(data.get("osurequestformat_osu", UNDEFINED))
		self.osurequestformat_twitch:str = self.asString(data.get("osurequestformat_twitch", UNDEFINED))
		self.owner_disable_level:bool = self.asBoolean(data.get("owner_disable_level", UNDEFINED))
		self.owner_disable_mod:bool = self.asBoolean(data.get("owner_disable_mod", UNDEFINED))
		self.owner_disable_normal:bool = self.asBoolean(data.get("owner_disable_normal", UNDEFINED))
		self.owner_disable_regular:bool = self.asBoolean(data.get("owner_disable_regular", UNDEFINED))
		self.punish_msg_caps:str = self.asString(data.get("punish_msg_caps", UNDEFINED))
		self.punish_msg_copypasta:str = self.asString(data.get("punish_msg_copypasta", UNDEFINED))
		self.punish_msg_emotes:str = self.asString(data.get("punish_msg_emotes", UNDEFINED))
		self.punish_msg_links:str = self.asString(data.get("punish_msg_links", UNDEFINED))
		self.punish_msg_unicode:str = self.asString(data.get("punish_msg_unicode", UNDEFINED))
		self.punish_msg_words:str = self.asString(data.get("punish_msg_words", UNDEFINED))
		self.punish_notify:bool = self.asBoolean(data.get("punish_notify", UNDEFINED))
		self.punish_option_caps:bool = self.asBoolean(data.get("punish_option_caps", UNDEFINED))
		self.punish_option_copypasta:bool = self.asBoolean(data.get("punish_option_copypasta", UNDEFINED))
		self.punish_option_emotes:bool = self.asBoolean(data.get("punish_option_emotes", UNDEFINED))
		self.punish_option_links:bool = self.asBoolean(data.get("punish_option_links", UNDEFINED))
		self.punish_option_unicode:bool = self.asBoolean(data.get("punish_option_unicode", UNDEFINED))
		self.punish_option_words:bool = self.asBoolean(data.get("punish_option_words", UNDEFINED))
		self.punish_timeout:int = self.asInteger(data.get("punish_timeout", UNDEFINED))

		# calc
		self.punish_wordblacklist:List[str] = self.fromStringList(data.get("punish_wordblacklist", UNDEFINED), separator=";;;")
		self.punish_linkwhitelist:List[str] = self.fromStringList(data.get("punish_linkwhitelist", UNDEFINED), separator=";;;")

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

		j["channel_id"] = self.asString(self.channel_id)

		j["active_game"] = self.asBoolean(self.active_game)
		j["active_level"] = self.asBoolean(self.active_level)
		j["active_quote"] = self.asBoolean(self.active_quote)
		j["currency_name"] = self.asString(self.currency_name)
		j["currency_name_multi"] = self.asString(self.currency_name_multi)
		j["gain_currency"] = self.asInteger(self.gain_currency)
		j["gain_currency_active_multi"] = self.asFloat(self.gain_currency_active_multi)
		j["gain_currency_message"] = self.asInteger(self.gain_currency_message)
		j["osurequestformat_osu"] = self.asString(self.osurequestformat_osu)
		j["osurequestformat_twitch"] = self.asString(self.osurequestformat_twitch)
		j["owner_disable_level"] = self.asBoolean(self.owner_disable_level)
		j["owner_disable_mod"] = self.asBoolean(self.owner_disable_mod)
		j["owner_disable_normal"] = self.asBoolean(self.owner_disable_normal)
		j["owner_disable_regular"] = self.asBoolean(self.owner_disable_regular)
		j["punish_msg_caps"] = self.asString(self.punish_msg_caps)
		j["punish_msg_copypasta"] = self.asString(self.punish_msg_copypasta)
		j["punish_msg_emotes"] = self.asString(self.punish_msg_emotes)
		j["punish_msg_links"] = self.asString(self.punish_msg_links)
		j["punish_msg_unicode"] = self.asString(self.punish_msg_unicode)
		j["punish_msg_words"] = self.asString(self.punish_msg_words)
		j["punish_notify"] = self.asBoolean(self.punish_notify)
		j["punish_option_caps"] = self.asBoolean(self.punish_option_caps)
		j["punish_option_copypasta"] = self.asBoolean(self.punish_option_copypasta)
		j["punish_option_emotes"] = self.asBoolean(self.punish_option_emotes)
		j["punish_option_links"] = self.asBoolean(self.punish_option_links)
		j["punish_option_unicode"] = self.asBoolean(self.punish_option_unicode)
		j["punish_option_words"] = self.asBoolean(self.punish_option_words)
		j["punish_timeout"] = self.asInteger(self.punish_timeout)

		return j
