from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.contentclass import ContentClass

class TwitchStream(ContentClass):
	"""
	Contains and represents a twitch stream
	"""
	def __init__(self, data:dict):

		self.user_id:str = self.asString(data.get("user_id", UNDEFINED))
		self.user_name:str = self.asString(data.get("user_name", UNDEFINED))
		self.game_id:str = self.asString(data.get("game_id", UNDEFINED))
		self.stream_type:str = self.asString(data.get("type", UNDEFINED))
		self.title:str = self.asString(data.get("title", UNDEFINED))
		self.viewer_count:int = self.asInteger(data.get("viewer_count", 0))
		self.language:str = self.asString(data.get("language", UNDEFINED))
		self.tags:list = self.asList(data.get("tags", UNDEFINED))
		self._thumbnail:str = self.asString(data.get("language", UNDEFINED))

	def __repr__(self):
		return f"<{self.__class__.__name__} user_id='{self.user_id}' game_id='{self.game_id}' type='{self.stream_type}'>"

	def thumbnail(self, w:int=1920) -> str:
		h:int = int(w/16*9)
		return self._thumbnail.format(width=w, height=h)

	def toJSON(self, thumbnail_width:int=1920) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["user_id"] = self.asString(self.user_id)
		j["user_name"] = self.asString(self.user_name)
		j["game_id"] = self.asString(self.game_id)
		j["stream_type"] = self.asString(self.stream_type)
		j["title"] = self.asString(self.title)
		j["viewer_count"] = self.asInteger(self.viewer_count)
		j["language"] = self.asString(self.language)
		j["thumbnail"] = self.asString(self.thumbnail(thumbnail_width))

		return j
