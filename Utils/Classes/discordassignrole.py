from Utils.Classes.undefined import Undefined
from Utils.Classes.dbcontentclass import DBContentClass

class DiscordAssignRole(DBContentClass):
	"""
		Contains and represents stuff for a discord assign role
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} server='{self.guild_id}' role_id='{self.role_id}' trigger='{self.trigger}'>"

	def __init__(self, data:dict, guild_id:str):

		self.assignrole_id:str = data.get("id", Undefined())
		self.guild_id:str = guild_id
		self.role_id:str = data.get("role_id", Undefined())
		self.trigger:str = data.get("trigger", Undefined())

	def toJSON(self) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["assignrole_id"] = str(self.assignrole_id)
		j["role_id"] = str(self.role_id)
		j["trigger"] = str(self.trigger)

		return j
