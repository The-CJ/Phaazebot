from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.dbcontentclass import DBContentClass
from Utils.Classes.apiclass import APIClass

class DiscordAssignRole(DBContentClass, APIClass):
	"""
		Contains and represents stuff for a discord assign role
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} server='{self.guild_id}' role_id='{self.role_id}' trigger='{self.trigger}'>"

	def __init__(self, data:dict, guild_id:str):

		self.assignrole_id:str = data.get("id", UNDEFINED)
		self.guild_id:str = guild_id
		self.role_id:str = data.get("role_id", UNDEFINED)
		self.trigger:str = data.get("trigger", UNDEFINED)

	def toJSON(self) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["assignrole_id"] = self.toString(self.assignrole_id)
		j["guild_id"] = self.toString(self.guild_id)
		j["role_id"] = self.toString(self.role_id)
		j["trigger"] = self.toString(self.trigger)

		return j
