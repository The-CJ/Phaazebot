from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.contentclass import ContentClass

class TwitchWebUser(ContentClass):
	"""
	Contains information's about a twitch web user,
	this object is suppose to be appended to a `AuthTwitchWebUser` object.

	(Don't get confused with `TwitchUser` object, these objects are used for general twitch api results)
	(TwitchWebUser is only used for a info storage for the current request twitch user)
	but i do admit... it's nearly the same.

	variable search way:
		System -> header/cookies
	"""
	def __init__(self, data:dict):
		self.user_id:str = self.asString(data.get("user_id", UNDEFINED))
		self.name:str = self.asString(data.get("name", UNDEFINED))
		self.display_name:str = self.asString(data.get("display_name", UNDEFINED))
		self.user_type:str = self.asString(data.get("user_id", UNDEFINED))
		self.broadcaster_type:str = self.asString(data.get("user_id", UNDEFINED))
		self.description:str = self.asString(data.get("user_id", UNDEFINED))
		self.profile_image_url:str = self.asString(data.get("user_id", UNDEFINED))
		self.offline_image_url:str = self.asString(data.get("user_id", UNDEFINED))
		self.view_count:int = self.asInteger(data.get("user_id", UNDEFINED))
		self.email:str = self.asString(data.get("user_id", UNDEFINED))

	def __repr__(self):
		return f"<{self.__class__.__name__} id='{self.user_id}' name='{self.name}'>"

	def toJSON(self, images:bool=True, types:bool=False) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["user_id"] = self.asString(self.user_id)
		j["name"] = self.asString(self.name)
		j["display_name"] = self.asString(self.display_name)
		j["description"] = self.asString(self.description)
		j["view_count"] = self.asInteger(self.view_count)
		j["email"] = self.asString(self.email)

		if images:
			j["profile_image_url"] = self.asString(self.profile_image_url)
			j["offline_image_url"] = self.asString(self.offline_image_url)

		if types:
			j["user_type"] = self.asString(self.user_type)
			j["broadcaster_type"] = self.asString(self.broadcaster_type)

		return j