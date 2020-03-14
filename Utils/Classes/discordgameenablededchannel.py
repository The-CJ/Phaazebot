from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.dbcontentclass import DBContentClass
from Utils.Classes.apiclass import APIClass

class DiscordGameEnabledChannel(DBContentClass, APIClass):
	"""
		Contains and represents stuff for a game enabled discord channel
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} server='{self.guild_id}' channel_id='{self.channel_id}'>"

	def __init__(self, data:dict, guild_id:str):

		self.guild_id:str = guild_id
		self.entry_id:int = data.get("id", UNDEFINED)
		self.channel_id:str = data.get("channel_id", UNDEFINED)

	def toJSON(self) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["entry_id"] = self.toString(self.entry_id)
		j["channel_id"] = self.toString(self.channel_id)

		return j
