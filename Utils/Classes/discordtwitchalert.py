from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.dbcontentclass import DBContentClass
from Utils.Classes.apiclass import APIClass

class DiscordTwitchAlert(DBContentClass, APIClass):
	"""
	Contains and represents stuff for a discord twitch alert
	"""
	def __init__(self, data:dict):

		# key
		self.alert_id:int = data.get("id", UNDEFINED)
		self.discord_channel_id:str = data.get("discord_channel_id", UNDEFINED)
		self.guild_id:str = data.get("discord_guild_id", UNDEFINED)
		self.twitch_channel_id:str = data.get("twitch_channel_id", UNDEFINED)

		# vars
		self.custom_msg:str = data.get("custom_msg", UNDEFINED)
		self.suppress_gamechange:bool = data.get("suppress_gamechange", UNDEFINED)
		self.twitch_channel_name:str = data.get("twitch_channel_name", UNDEFINED)

	def __repr__(self):
		return f"<{self.__class__.__name__} discord_channel_id='{self.discord_channel_id}' twitch_channel_id={self.twitch_channel_id}>"

	def toJSON(self, custom_msg:bool=False) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["alert_id"] = self.toString(self.alert_id)
		j["discord_channel_id"] = self.toString(self.discord_channel_id)
		j["guild_id"] = self.toString(self.guild_id)
		j["twitch_channel_id"] = self.toString(self.twitch_channel_id)
		j["suppress_gamechange"] = self.toBoolean(self.suppress_gamechange)
		j["twitch_channel_name"] = self.toString(self.twitch_channel_name)

		if custom_msg:
			j["custom_msg"] = self.toString(self.custom_msg)

		return j
