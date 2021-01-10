from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.contentclass import ContentClass

class DiscordRegular(ContentClass):
	"""
	Contains and represents stuff for a discord member that is a regular
	"""
	def __init__(self, data:dict):

		# key
		self.regular_id:int = self.asInteger(data.get("id", UNDEFINED))
		self.guild_id:str = self.asString(data.get("guild_id", UNDEFINED))

		# vars
		self.member_id:str = self.asString(data.get("member_id", UNDEFINED))

	def __repr__(self):
		return f"<{self.__class__.__name__} server='{self.guild_id}' member='{self.member_id}'>"

	def toJSON(self) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["regular_id"] = self.asString(self.regular_id)
		j["guild_id"] = self.asString(self.guild_id)
		j["member_id"] = self.asString(self.member_id)

		return j
