from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.dbcontentclass import DBContentClass
from Utils.Classes.apiclass import APIClass

class DiscordQuote(DBContentClass, APIClass):
	"""
		Contains and represents stuff for a discord quote
	"""
	def __init__(self, data:dict, guild_id:str):

		self.guild_id:str = guild_id
		self.quote_id:str = data.get("id", UNDEFINED)
		self.content:str = data.get("content", UNDEFINED)

	def __repr__(self):
		return f"<{self.__class__.__name__} server='{self.guild_id}' quote='{self.quote_id}'>"

	def toJSON(self) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["quote_id"] = self.toString(self.quote_id)
		j["guild_id"] = self.toString(self.guild_id)
		j["content"] = self.toString(self.content)

		return j
