from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.contentclass import ContentClass

class DiscordUserMedal(ContentClass):
	"""
	Contains and represents stuff for a discord user medal
	"""
	def __init__(self, data:dict):

		self.medal_id:int = self.asInteger(data.get("id", UNDEFINED))
		self.guild_id:str = self.asString(data.get("guild_id", UNDEFINED))
		self.member_id:str = self.asString(data.get("member_id", UNDEFINED))
		self.name:str = self.asString(data.get("name", UNDEFINED))

	def __repr__(self):
		return f"<{self.__class__.__name__} server='{self.guild_id}' medal='{self.medal_id}'>"

	def toJSON(self) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["medal_id"] = self.asString(self.medal_id)
		j["guild_id"] = self.asString(self.guild_id)
		j["member_id"] = self.asString(self.member_id)
		j["name"] = self.asString(self.name)

		return j
