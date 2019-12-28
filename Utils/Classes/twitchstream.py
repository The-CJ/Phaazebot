from Utils.Classes.undefined import UNDEFINED

class TwitchStream(object):
	"""
		Contains and represents a twitch stream
	"""
	def __init__(self, data:dict):

		self.user_id:str = data.get("user_id", UNDEFINED)
		self.user_name:str = data.get("user_name", UNDEFINED)
		self.game_id:str = data.get("game_id", UNDEFINED)
		self.stream_type:str = data.get("type", UNDEFINED)
		self.title:str = data.get("title", UNDEFINED)
		self.viewer_count:int = data.get("viewer_count", 0)
		self.language:str = data.get("language", UNDEFINED)
		self.tags:list = data.get("language", UNDEFINED)
		self._thumbnail:str = data.get("language", UNDEFINED)

	def __repr__(self):
		return f"<{self.__class__.__name__} user_id='{self.user_id}' game_id='{self.game_id}' type='{self.stream_type}'>"

	def thumbnail(self, w:int=1920) -> str:
		h:int = int(w/16*9)
		return self._thumbnail.format(width=w, height=h)

	def toJSON(self) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["user_id"] = self.user_id
		j["user_name"] = self.user_name
		j["game_id"] = self.game_id
		j["stream_type"] = self.stream_type
		j["title"] = self.title
		j["viewer_count"] = self.viewer_count
		j["language"] = self.language
		j["thumbnail"] = self.thumbnail()

		return j
