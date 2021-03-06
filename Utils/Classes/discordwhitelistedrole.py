from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.contentclass import ContentClass

class DiscordWhitelistedRole(ContentClass):
	"""
	Contains and represents a whitelisted role in discord
	Whitelisted means there are a exception to the blacklist and spam filter
	"""
	def __init__(self, data:dict):

		# key
		self.exceptionrole_id:int = self.asInteger(data.get("id", UNDEFINED))
		self.guild_id:str = self.asString(data.get("guild_id", UNDEFINED))

		# vars
		self.role_id:str = self.asString(data.get("role_id", UNDEFINED))

	def __repr__(self):
		return f"<{self.__class__.__name__} server='{self.guild_id}' role_id='{self.role_id}'>"

	def toJSON(self) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["exceptionrole_id"] = self.asString(self.exceptionrole_id)
		j["role_id"] = self.asString(self.role_id)

		return j
