from typing import List
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
		self.punish_msg_caps:str = infos.get("punish_msg_caps", UNDEFINED)
		self.punish_msg_copypasta:str = infos.get("punish_msg_copypasta", UNDEFINED)
		self.punish_msg_emotes:str = infos.get("punish_msg_emotes", UNDEFINED)
		self.punish_msg_links:str = infos.get("punish_msg_links", UNDEFINED)
		self.punish_msg_unicode:str = infos.get("punish_msg_unicode", UNDEFINED)
		self.punish_msg_words:str = infos.get("punish_msg_words", UNDEFINED)
		self.punish_notify:bool = bool( infos.get("punish_notify", UNDEFINED) )
		self.punish_option_caps:bool = bool( infos.get("punish_option_caps", UNDEFINED) )
		self.punish_option_copypasta:bool = bool( infos.get("punish_option_copypasta", UNDEFINED) )
		self.punish_option_emotes:bool = bool( infos.get("punish_option_emotes", UNDEFINED) )
		self.punish_option_links:bool = bool( infos.get("punish_option_links", UNDEFINED) )
		self.punish_option_unicode:bool = bool( infos.get("punish_option_unicode", UNDEFINED) )
		self.punish_option_words:bool = bool( infos.get("punish_option_words", UNDEFINED) )
		self.punish_timeout:int = infos.get("punish_timeout", UNDEFINED)

		# calc
		self.punish_wordblacklist:List[str] = self.fromStringList( infos.get("punish_wordblacklist", UNDEFINED), seperator=";;;" )

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

		j["channel_id"] = self.toString(self.channel_id)

		j["active_game"] = self.toBoolean(self.active_game)
		j["active_level"] = self.toBoolean(self.active_level)
		j["active_quote"] = self.toBoolean(self.active_quote)
		j["currency_name"] = self.toString(self.currency_name)
		j["currency_name_multi"] = self.toString(self.currency_name_multi)
		j["gain_currency"] = self.toInteger(self.gain_currency)
		j["gain_currency_active_multi"] = self.toFloat(self.gain_currency_active_multi)
		j["gain_currency_message"] = self.toInteger(self.gain_currency_message)
		j["osurequestformat_osu"] = self.toString(self.osurequestformat_osu)
		j["osurequestformat_twtich"] = self.toString(self.osurequestformat_twtich)
		j["owner_disable_level"] = self.toBoolean(self.owner_disable_level)
		j["owner_disable_mod"] = self.toBoolean(self.owner_disable_mod)
		j["owner_disable_normal"] = self.toBoolean(self.owner_disable_normal)
		j["owner_disable_regular"] = self.toBoolean(self.owner_disable_regular)
		j["punish_msg_caps"] = self.toString(self.punish_msg_caps)
		j["punish_msg_copypasta"] = self.toString(self.punish_msg_copypasta)
		j["punish_msg_emotes"] = self.toString(self.punish_msg_emotes)
		j["punish_msg_links"] = self.toString(self.punish_msg_links)
		j["punish_msg_unicode"] = self.toString(self.punish_msg_unicode)
		j["punish_msg_words"] = self.toString(self.punish_msg_words)
		j["punish_notify"] = self.toBoolean(self.punish_notify)
		j["punish_option_caps"] = self.toBoolean(self.punish_option_caps)
		j["punish_option_copypasta"] = self.toBoolean(self.punish_option_copypasta)
		j["punish_option_emotes"] = self.toBoolean(self.punish_option_emotes)
		j["punish_option_links"] = self.toBoolean(self.punish_option_links)
		j["punish_option_unicode"] = self.toBoolean(self.punish_option_unicode)
		j["punish_option_words"] = self.toBoolean(self.punish_option_words)
		j["punish_timeout"] = self.toInteger(self.punish_timeout)

		return j
