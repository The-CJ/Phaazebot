from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.apiclass import APIClass

class TwitchUser(APIClass):
	"""
		Contains and represents a twitch user

	"""
	def __init__(self, data:dict):

		self.user_id:str = data.get("id", UNDEFINED)
		self.name:str = data.get("login", UNDEFINED)
		self.display_name:str = data.get("display_name", UNDEFINED)
		self.user_type:str = data.get("type", UNDEFINED)
		self.broadcaster_type:str = data.get("broadcaster_type", UNDEFINED)
		self.description:str = data.get("description", UNDEFINED)
		self.profile_image_url:str = data.get("profile_image_url", UNDEFINED)
		self.offline_image_url:str = data.get("offline_image_url", UNDEFINED)
		self.view_count:int = int( data.get("view_count", UNDEFINED) )

	def __repr__(self):
		return f"<{self.__class__.__name__} user_id='{self.user_id}' name='{self.name}'>"

	def toJSON(self, types:bool=True, images:bool=False) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["user_id"] = self.toString(self.user_id)
		j["name"] = self.toString(self.name)
		j["display_name"] = self.toString(self.display_name)
		j["description"] = self.toString(self.description)
		j["view_count"] = self.toInteger(self.view_count)

		if types:
			j["user_type"] = self.toString(self.user_type)
			j["broadcaster_type"] = self.toString(self.broadcaster_type)

		if images:
			j["profile_image_url"] = self.toString(self.profile_image_url)
			j["offline_image_url"] = self.toString(self.offline_image_url)

		return j
