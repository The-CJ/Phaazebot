from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.dbcontentclass import DBContentClass
from Utils.Classes.apiclass import APIClass

class DiscordWhitelistedLink(DBContentClass, APIClass):
	"""
	Contains and represents a whitelisted link in discord
	Whitelisted means that even if links are banned, this link (regex)
	is a allowed exception
	"""
	def __init__(self, data:dict, guild_id:str):

		self.guild_id:str = guild_id
		self.link_id:int = data.get("id", UNDEFINED)
		self.link:str = data.get("link", UNDEFINED)

	def __repr__(self):
		return f"<{self.__class__.__name__} server='{self.guild_id}' link_id='{self.link_id}'>"

	def toJSON(self) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["link_id"] = self.toString(self.link_id)
		j["link"] = self.toString(self.link)

		return j
