from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.contentclass import ContentClass

class DiscordAssignRole(ContentClass):
	"""
	Contains and represents stuff for a discord assign role
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} server='{self.guild_id}' role_id='{self.role_id}' trigger='{self.trigger}'>"

	def __init__(self, data:dict):

		# key
		self.assignrole_id:int = self.asInteger(data.get("id", UNDEFINED))
		self.guild_id:str = self.asString(data.get("guild_id", UNDEFINED))

		# vars
		self.role_id:str = self.asString(data.get("role_id", UNDEFINED))
		self.trigger:str = self.asString(data.get("trigger", UNDEFINED))

	def toJSON(self) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["assignrole_id"] = self.asString(self.assignrole_id)
		j["role_id"] = self.asString(self.role_id)
		j["trigger"] = self.asString(self.trigger)

		return j
