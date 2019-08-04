from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

from .undefined import Undefined
from Utils.Classes.dbcontentclass import DBContentClass

class DiscordCommand(DBContentClass):
	def __repr__(self):
		return f"<{self.__class__.__name__} server='{self.server_id}' trigger='{self.trigger}'>"

	def __init__(self, data:dict, server_id:str):
		self.server_id:str = server_id
		self.command_id:int = data.get("id", Undefined())
		self.trigger:str = data.get("trigger", Undefined())
		self.complex:bool = data.get("complex", False)
		self.description:str = self.getDescription()
		self.content:str = data.get("content", Undefined())
		self.uses:int = data.get("uses", 0)
		self.function:str = data.get("function", Undefined())
		self.require:int = data.get("require", 0)
		self.required_currency:int = data.get("required_currency", 0)
		self.hidden:bool = data.get("hidden", False)

	async def increaseUse(self, cls:"PhaazebotDiscord", by:int=1) -> None:
		cls.BASE.PhaazeDB.query("""
			UPDATE discord_command
			SET uses = uses + %s
			WHERE id = %s""",
			(by, self.command_id)
		)

		cls.BASE.Logger.debug(f"(Discord) Increase command: {self.trigger} -> x{self.uses+by}", require="discord:command")

	def getDescription(self) -> str:
		if self.complex:
			return 0 # return complex str
