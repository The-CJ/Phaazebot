import datetime
from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.contentclass import ContentClass

from Platforms.Discord.logging import TRACK_OPTIONS

class DiscordLog(ContentClass):
	"""
	Contains and represents stuff for a discord log entry
	"""
	def __init__(self, data:dict):

		# key
		self.log_id:int = data.get("id", UNDEFINED)
		self.guild_id:str = data.get("guild_id", UNDEFINED)

		# vars
		self.content:str = data.get("content", UNDEFINED)
		self.created_at:datetime.datetime = data.get("created_at", UNDEFINED)
		self.event_value:int = data.get("event_value", UNDEFINED)
		self.initiator_id:str = data.get("initiator_id", UNDEFINED)

	def __repr__(self):
		return f"<{self.__class__.__name__} server='{self.guild_id}' log='{self.log_id}'>"

	def toJSON(self) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["log_id"] = self.asString(self.log_id)
		j["content"] = self.asString(self.content)
		j["created_at"] = self.asString(self.created_at)
		j["event_name"] = self.asString(self.event_name)
		j["event_value"] = self.asInteger(self.event_value)
		j["initiator_id"] = self.asString(self.initiator_id)

		return j

	@property
	def event_name(self) -> str:

		for name in TRACK_OPTIONS:
			value:int = TRACK_OPTIONS[name]
			if self.event_value == value: return name

		return "Unknown"
