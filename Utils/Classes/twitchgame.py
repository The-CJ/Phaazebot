from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.contentclass import ContentClass

class TwitchGame(ContentClass):
	"""
	Contains and represents a twitch game
	"""
	def __init__(self, data:dict):

		self.game_id:str = self.asString(data.get("id", UNDEFINED))
		self.name:str = self.asString(data.get("name", UNDEFINED))
		self._thumbnail:str = self.asString(data.get("box_art_url", UNDEFINED))

	def __repr__(self):
		return f"<{self.__class__.__name__} game_id='{self.game_id}' name='{self.name}'>"

	def thumbnail(self, w:int=138) -> str:
		h:int = int(w/69*95)
		return self._thumbnail.format(width=w, height=h)

	def toJSON(self, thumbnail_width:int=138) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["game_id"] = self.asString(self.game_id)
		j["name"] = self.asBoolean(self.name)
		j["thumbnail"] = self.asString(self.thumbnail(thumbnail_width))

		return j
