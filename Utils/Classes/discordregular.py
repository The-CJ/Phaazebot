from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.dbcontentclass import DBContentClass
from Utils.Classes.apiclass import APIClass

class DiscordRegular(DBContentClass, APIClass):
	"""
	Contains and represents stuff for a discord member that is a regular
	"""
	def __init__(self, data:dict):

		self.regular_id:str = data.get("id", UNDEFINED)
		self.guild_id:str = data.get("guild_id", UNDEFINED)
		self.member_id:int =data.get("member_id", UNDEFINED)

	def __repr__(self):
		return f"<{self.__class__.__name__} server='{self.guild_id}' member='{self.member_id}'>"

	def toJSON(self) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["regular_id"] = self.toString(self.regular_id)
		j["guild_id"] = self.toString(self.guild_id)
		j["member_id"] = self.toString(self.member_id)

		return j
