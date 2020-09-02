import datetime
from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.dbcontentclass import DBContentClass
from Utils.Classes.apiclass import APIClass

from Platforms.Discord.logging import TRACK_OPTIONS

class DiscordLog(DBContentClass, APIClass):
	"""
	Contains and represents stuff for a discord log entry
	"""
	def __init__(self, data:dict, guild_id:str):

		self.guild_id:str = guild_id
		self.log_id:int = data.get("id", UNDEFINED)
		self.event_value:int = data.get("event_value", UNDEFINED)
		self.created_at:datetime.datetime = data.get("created_at", UNDEFINED)
		self.initiator_id:str = data.get("initiator_id", UNDEFINED)
		self.content:str = data.get("content", UNDEFINED)

	def __repr__(self):
		return f"<{self.__class__.__name__} server='{self.guild_id}' log='{self.log_id}'>"

	def toJSON(self) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["log_id"] = self.toString(self.log_id)
		j["guild_id"] = self.toString(self.guild_id)
		j["event_value"] = self.toInteger(self.event_value)
		j["event_name"] = self.toString(self.event_name)
		j["created_at"] = self.toString(self.created_at)
		j["initiator_id"] = self.toString(self.initiator_id)
		j["content"] = self.toString(self.content)

		return j

	@property
	def event_name(self) -> str:

		for name in TRACK_OPTIONS:
			value:int = TRACK_OPTIONS[name]
			if self.event_value == value: return name

		return "Unknown"
