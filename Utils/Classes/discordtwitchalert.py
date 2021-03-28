from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.contentclass import ContentClass

class DiscordTwitchAlert(ContentClass):
	"""
	Contains and represents stuff for a discord twitch alert
	"""
	def __init__(self, data:dict):

		# key
		self.alert_id:int = self.asInteger(data.get("id", UNDEFINED))
		self.discord_channel_id:str = self.asString(data.get("discord_channel_id", UNDEFINED))
		self.guild_id:str = self.asString(data.get("discord_guild_id", UNDEFINED))
		self.twitch_channel_id:str = self.asString(data.get("twitch_channel_id", UNDEFINED))

		# vars
		self.custom_msg:str = self.asString(data.get("custom_msg", UNDEFINED))
		self.suppress_gamechange:bool = self.asBoolean(data.get("suppress_gamechange", UNDEFINED))
		self.twitch_channel_name:str = self.asString(data.get("twitch_channel_name", UNDEFINED))

	def __repr__(self):
		return f"<{self.__class__.__name__} discord_channel_id='{self.discord_channel_id}' twitch_channel_id={self.twitch_channel_id}>"

	def toJSON(self, custom_msg:bool=False) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["alert_id"] = self.asString(self.alert_id)
		j["discord_channel_id"] = self.asString(self.discord_channel_id)
		j["guild_id"] = self.asString(self.guild_id)
		j["twitch_channel_id"] = self.asString(self.twitch_channel_id)
		j["suppress_gamechange"] = self.asBoolean(self.suppress_gamechange)
		j["twitch_channel_name"] = self.asString(self.twitch_channel_name)

		if custom_msg:
			j["custom_msg"] = self.asString(self.custom_msg)

		return j
