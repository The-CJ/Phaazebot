from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

from .undefined import Undefined

class DiscordCommand(object):
	def __repr__(self):
		return f"<{self.__class__.__name__} server='{self.server_id}' trigger='{self.trigger}'>"

	def __init__(self, data:dict, server_id:str):
		self.server_id:str = server_id
		self.command_id:int = data.get("id", Undefined())
		self.trigger:str = data.get("trigger", Undefined())
		self.content:str = data.get("content", Undefined())
		self.uses:int = data.get("uses", 0)
		self.complex:bool = data.get("complex", False)
		self.function:str = data.get("function", Undefined())
		self.require:int = data.get("require", 0)

	async def increaseUse(self, cls:"PhaazebotDiscord", by:int=1) -> None:
		self.uses = self.uses + 1
		res:dict = cls.BASE.PhaazeDB.update(
			of = f"discord/commands/commands_{self.server_id}",
			where = f"int(data['id']) == int({self.command_id})",
			content = {"uses": self.uses}
		)

		if res.get("status", "error") == "error":
			cls.BASE.Logger.error(f"(Discord) Increase command use failed")
			raise RuntimeError("Increasing Discord command use failed")

		cls.BASE.Logger.debug(f"(Discord) Increase command: {self.trigger}", require="discord:command")
