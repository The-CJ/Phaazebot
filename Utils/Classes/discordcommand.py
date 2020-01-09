from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.dbcontentclass import DBContentClass
from Utils.Classes.storeclasses import GlobalStorage

class DiscordCommand(DBContentClass):
	def __init__(self, data:dict, server_id:str):
		self.server_id:str = server_id
		self.command_id:str = data.get("id", UNDEFINED)

		self.trigger:str = data.get("trigger", UNDEFINED)
		self.active:bool = bool( data.get("active", 1) )
		self.complex:bool = data.get("complex", False)
		self.function:str = data.get("function", UNDEFINED)
		self.content:str = data.get("content", UNDEFINED)
		self.uses:int = data.get("uses", 0)
		self.require:int = data.get("require", 0)
		self.required_currency:int = data.get("required_currency", 0)
		self.hidden:bool = bool( data.get("hidden", False) )
		self.cooldown:int = data.get("cooldown", 0)

	def __repr__(self):
		return f"<{self.__class__.__name__} server='{self.server_id}' trigger='{self.trigger}'>"

	def toJSON(self, show_hidden:bool=False) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["command_id"] = str(self.command_id)
		j["trigger"] = str(self.trigger)
		j["active"] = bool(self.active)
		j["complex"] = bool(self.complex)
		j["uses"] = int(self.uses)
		j["require"] = int(self.require)
		j["cost"] = int(self.required_currency)
		j["cooldown"] = int(self.cooldown)
		j["hidden"] = bool(self.hidden)

		if show_hidden or not self.hidden:
			j["function"] = str(self.function)
			j["content"] = str(self.content)
			j["name"] = str(self.name)
			j["description"] = str(self.description)

		else:
			j["function"] = None
			j["content"] = None
			j["name"] = None
			j["description"] = None

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
