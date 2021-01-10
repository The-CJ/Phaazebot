from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.contentclass import ContentClass
from Utils.Classes.apiclass import APIClass

class WebRole(ContentClass, APIClass):
	"""
	Contains and represents a role for the web server
	"""
	def __init__(self, data:dict):

		# key
		self.role_id:int = data.get("id", UNDEFINED)
		self.can_be_removed:bool = bool( data.get("can_be_removed", UNDEFINED) )
		self.description:str = data.get("description", UNDEFINED)
		self.name:str = data.get("name", UNDEFINED)

	def __repr__(self):
		return f"<{self.__class__.__name__} id='{self.guild_id}' name='{self.role_id}'>"

	def toJSON(self) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["role_id"] = self.toString(self.role_id)
		j["can_be_removed"] = self.toBoolean(self.can_be_removed)
		j["description"] = self.toString(self.description)
		j["name"] = self.toString(self.name)

		return j
