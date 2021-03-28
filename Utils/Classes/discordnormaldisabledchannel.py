from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.contentclass import ContentClass

class DiscordNormalDisabledChannel(ContentClass):
	"""
	Contains and represents stuff for a normal disabled discord channel
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} server='{self.guild_id}' channel_id='{self.channel_id}'>"

	def __init__(self, data:dict):

		# key
		self.entry_id:int = self.asInteger(data.get("id", UNDEFINED))
		self.guild_id:str = self.asString(data.get("guild_id", UNDEFINED))

		# vars
		self.channel_id:str = self.asString(data.get("channel_id", UNDEFINED))

	def toJSON(self) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["entry_id"] = self.asString(self.entry_id)
		j["channel_id"] = self.asString(self.channel_id)

		return j
