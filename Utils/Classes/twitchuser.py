from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.contentclass import ContentClass

class TwitchUser(ContentClass):
	"""
	Contains and represents a twitch user.
	If extended is true, it's a authorised user entry.
	"""
	def __init__(self, data:dict):
		self.user_id:str = self.asString(data.get("id", UNDEFINED))
		self.login:str = self.asString(data.get("login", UNDEFINED))
		self.display_name:str = self.asString(data.get("display_name", UNDEFINED))
		self.user_type:str = self.asString(data.get("type", UNDEFINED))
		self.broadcaster_type:str = self.asString(data.get("broadcaster_type", UNDEFINED))
		self.description:str = self.asString(data.get("description", UNDEFINED))
		self.profile_image_url:str = self.asString(data.get("profile_image_url", UNDEFINED))
		self.offline_image_url:str = self.asString(data.get("offline_image_url", UNDEFINED))
		self.view_count:int = self.asInteger(data.get("view_count", UNDEFINED))
		self.email:str = self.asString(data.get("email", UNDEFINED))

		self.extended:bool = bool(self.email)

		if not self.user_id:  # because i messed things up in the long game
			self.user_id: str = self.asString(data.get("user_id", UNDEFINED))

	def __repr__(self):
		if self.extended:
			return f"<{self.__class__.__name__} [extended] user_id='{self.user_id}' login='{self.login}'>"

		return f"<{self.__class__.__name__} user_id='{self.user_id}' login='{self.login}'>"

	def toJSON(self, types:bool=True, images:bool=True, with_email:bool=True) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["user_id"] = self.asString(self.user_id)
		j["login"] = self.asString(self.login)
		j["display_name"] = self.asString(self.display_name)
		j["description"] = self.asString(self.description)
		j["view_count"] = self.asInteger(self.view_count)

		if types:
			j["user_type"] = self.asString(self.user_type)
			j["broadcaster_type"] = self.asString(self.broadcaster_type)

		if images:
			j["profile_image_url"] = self.asString(self.profile_image_url)
			j["offline_image_url"] = self.asString(self.offline_image_url)

		if with_email and self.email:
			j["email"] = self.asString(self.email)

		return j
