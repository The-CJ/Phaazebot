from Utils.Classes.undefined import UNDEFINED

class TwitchUser(object):
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

		j["user_id"] = str(self.user_id)
		j["name"] = str(self.name)
		j["display_name"] = str(self.display_name)
		j["description"] = str(self.description)
		j["view_count"] = int(self.view_count)

		if types:
			j["user_type"] = str(self.user_type)
			j["broadcaster_type"] = str(self.broadcaster_type)

		if images:
			j["profile_image_url"] = str(self.profile_image_url)
			j["offline_image_url"] = str(self.offline_image_url)

		return j
