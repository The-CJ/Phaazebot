from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.dbcontentclass import DBContentClass
from Utils.Classes.apiclass import APIClass

class DiscordUserMedal(DBContentClass, APIClass):
	"""
	Contains and represents stuff for a discord user medal
	"""
	def __init__(self, data:dict, guild_id:str):

		self.guild_id:str = guild_id
		self.medal_id:int = data.get("id", UNDEFINED)
		self.member_id:int = data.get("member_id", UNDEFINED)
		self.name:str = data.get("name", UNDEFINED)

	def __repr__(self):
		return f"<{self.__class__.__name__} server='{self.guild_id}' medal='{self.medal_id}'>"

	def toJSON(self) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["medal_id"] = self.toString(self.medal_id)
		j["guild_id"] = self.toString(self.guild_id)
		j["member_id"] = self.toString(self.member_id)
		j["name"] = self.toString(self.name)

		return j
