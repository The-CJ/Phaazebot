from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.dbcontentclass import DBContentClass
from Utils.Classes.apiclass import APIClass
from Utils.Classes.storeclasses import GlobalStorage

class DiscordCommand(DBContentClass, APIClass):
	"""
	Contains and represents a discord command
	"""
	def __init__(self, data:dict):

		# key
		self.command_id:int = data.get("id", UNDEFINED)
		self.server_id:str = data.get("guild_id", UNDEFINED)
		self.guild_id:str = data.get("guild_id", UNDEFINED)
		self.trigger:str = data.get("trigger", UNDEFINED)

		# vars
		self.active:bool = bool( data.get("active", 1) )
		self.complex:bool = bool( data.get("complex", False) )
		self.content:str = data.get("content", UNDEFINED)
		self.cooldown:int = data.get("cooldown", 0)
		self.function:str = data.get("function", UNDEFINED)
		self.hidden:bool = bool( data.get("hidden", False) )
		self.require:int = data.get("require", 0)
		self.required_currency:int = data.get("required_currency", 0)
		self.uses:int = data.get("uses", 0)

	def __repr__(self):
		return f"<{self.__class__.__name__} server='{self.server_id}' trigger='{self.trigger}'>"

	def toJSON(self, show_hidden:bool=False) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["active"] = self.toBoolean(self.active)
		j["command_id"] = self.toString(self.command_id)
		j["complex"] = self.toBoolean(self.complex)
		j["cooldown"] = self.toInteger(self.cooldown)
		j["cost"] = self.toInteger(self.required_currency)
		j["hidden"] = self.toBoolean(self.hidden)
		j["require"] = self.toInteger(self.require)
		j["trigger"] = self.toString(self.trigger)
		j["uses"] = self.toInteger(self.uses)

		if show_hidden or not self.hidden:
			j["content"] = self.toString(self.content)
			j["description"] = self.toString(self.description)
			j["function"] = self.toString(self.function)
			j["name"] = self.toString(self.name)

		else:
			j["content"] = None
			j["description"] = None
			j["function"] = None
			j["name"] = None

		return j

	async def increaseUse(self, cls:"PhaazebotDiscord", by:int=1) -> None:
		cls.BASE.PhaazeDB.query("""
			UPDATE `discord_command`
			SET `uses` = `uses` + %s
			WHERE `id` = %s""",
			(by, self.command_id)
		)

		cls.BASE.Logger.debug(f"(Discord) Increase command: S:{self.server_id} C:{self.command_id} -> x{self.uses+by}", require="discord:command")

	@property
	def name(self) -> str:
		if self.complex:
			return "Complex function"

		else:
			command_register:list = GlobalStorage.get("discord_command_register", [])
			for cmd in command_register:
				if cmd["function"].__name__ == self.function: return cmd["name"]

			return "Unknown"

	@property
	def description(self) -> str:
		if self.complex:
			return "This is a complex function, it could be, that this function does a lot of things, or very less, how knows"

		else:
			command_register:list = GlobalStorage.get("discord_command_register", [])
			for cmd in command_register:
				if cmd["function"].__name__ == self.function: return cmd["description"]

			return "Unknown"
