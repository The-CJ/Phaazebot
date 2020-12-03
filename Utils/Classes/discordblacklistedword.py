from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.dbcontentclass import DBContentClass
from Utils.Classes.apiclass import APIClass

class DiscordBlacklistedWord(DBContentClass, APIClass):
	"""
	Contains and represents a blacklisted word in discord
	"""
	def __init__(self, data:dict):

		# key
		self.word_id:int = data.get("id", UNDEFINED)
		self.guild_id:str = data.get("guild_id", UNDEFINED)

		# vars
		self.word:str = data.get("word", UNDEFINED)

	def __repr__(self):
		return f"<{self.__class__.__name__} server='{self.guild_id}' word='{self.word_id}'>"

	def toJSON(self) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["word_id"] = self.toString(self.word_id)
		j["word"] = self.toString(self.word)

		return j
