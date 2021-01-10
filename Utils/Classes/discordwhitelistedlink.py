from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.contentclass import ContentClass
from Utils.Classes.apiclass import APIClass

class DiscordWhitelistedLink(ContentClass, APIClass):
	"""
	Contains and represents a whitelisted link in discord
	Whitelisted means that even if links are banned, this link (regex)
	is a allowed exception
	"""
	def __init__(self, data:dict):

		# key
		self.link_id:int = data.get("id", UNDEFINED)
		self.guild_id:str = data.get("guild_id", UNDEFINED)

		# vars
		self.link:str = data.get("link", UNDEFINED)

	def __repr__(self):
		return f"<{self.__class__.__name__} server='{self.guild_id}' link_id='{self.link_id}'>"

	def toJSON(self) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["link_id"] = self.toString(self.link_id)
		j["link"] = self.toString(self.link)

		return j
