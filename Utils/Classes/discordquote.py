from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.contentclass import ContentClass

class DiscordQuote(ContentClass):
	"""
	Contains and represents stuff for a discord quote
	"""
	def __init__(self, data:dict):

		# key
		self.quote_id:int = self.asInteger(data.get("id", UNDEFINED))
		self.guild_id:str = self.asString(data.get("guild_id", UNDEFINED))

		# vars
		self.content:str = self.asString(data.get("content", UNDEFINED))

	def __repr__(self):
		return f"<{self.__class__.__name__} server='{self.guild_id}' quote='{self.quote_id}'>"

	def toJSON(self) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["quote_id"] = self.asString(self.quote_id)
		j["guild_id"] = self.asString(self.guild_id)
		j["content"] = self.asString(self.content)

		return j
