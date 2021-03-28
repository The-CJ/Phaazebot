from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.contentclass import ContentClass

class WebRole(ContentClass):
	"""
	Contains and represents a role for the web server
	"""
	def __init__(self, data:dict):

		# key
		self.role_id:int = self.asInteger(data.get("id", UNDEFINED))
		self.can_be_removed:bool = self.asBoolean(data.get("can_be_removed", UNDEFINED))
		self.description:str = self.asString(data.get("description", UNDEFINED))
		self.name:str = self.asString(data.get("name", UNDEFINED))

	def __repr__(self):
		return f"<{self.__class__.__name__} id='{self.role_id}' name='{self.name}'>"

	def toJSON(self) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["role_id"] = self.asString(self.role_id)
		j["can_be_removed"] = self.asBoolean(self.can_be_removed)
		j["description"] = self.asString(self.description)
		j["name"] = self.asString(self.name)

		return j
