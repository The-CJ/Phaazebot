from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

from .undefined import Undefined
from Utils.Classes.dbcontentclass import DBContentClass
from Utils.Classes.storeclasses import GlobalStorage

class DiscordCommand(DBContentClass):
	def __init__(self, data:dict, server_id:str):
		self.server_id:str = server_id
		self.command_id:int = data.get("id", Undefined())

		self.trigger:str = data.get("trigger", Undefined())
		self.complex:bool = data.get("complex", False)
		self.function:str = data.get("function", Undefined())
		self.content:str = data.get("content", Undefined())
		self.uses:int = data.get("uses", 0)
		self.require:int = data.get("require", 0)
		self.required_currency:int = data.get("required_currency", 0)
		self.hidden:bool = data.get("hidden", False)
		self.cooldown:int = data.get("cooldown", 0)

	def __repr__(self):
		return f"<{self.__class__.__name__} server='{self.server_id}' trigger='{self.trigger}'>"

	def toJSON(self) -> dict:
		pass

	async def increaseUse(self, cls:"PhaazebotDiscord", by:int=1) -> None:
		cls.BASE.PhaazeDB.query("""
			UPDATE `discord_command`
			SET `uses` = `uses` + %s
			WHERE `id` = %s""",
			(by, self.command_id)
		)

		cls.BASE.Logger.debug(f"(Discord) Increase command: {self.trigger} ({self.command_id}) -> x{self.uses+by}", require="discord:command")

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
