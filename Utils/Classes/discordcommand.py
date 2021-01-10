from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.contentclass import ContentClass
from Utils.Classes.storeclasses import GlobalStorage

class DiscordCommand(ContentClass):
	"""
	Contains and represents a discord command
	"""
	def __init__(self, data:dict):

		# key
		self.command_id:int = self.asInteger(data.get("id", UNDEFINED))
		self.server_id:str = self.asString(data.get("guild_id", UNDEFINED))
		self.guild_id:str = self.asString(data.get("guild_id", UNDEFINED))
		self.trigger:str = self.asString(data.get("trigger", UNDEFINED))

		# vars
		self.active:bool = self.asBoolean(data.get("active", True))
		self.complex:bool = self.asBoolean(data.get("complex", False))
		self.content:str = self.asString(data.get("content", UNDEFINED))
		self.cooldown:int = self.asInteger(data.get("cooldown", UNDEFINED))
		self.function:str = self.asString(data.get("function", UNDEFINED))
		self.hidden:bool = self.asBoolean(data.get("hidden", False))
		self.require:int = self.asInteger(data.get("require", 0))
		self.required_currency:int = self.asInteger(data.get("required_currency", 0))
		self.uses:int = self.asInteger(data.get("uses", 0))

	def __repr__(self):
		return f"<{self.__class__.__name__} server='{self.server_id}' trigger='{self.trigger}'>"

	def toJSON(self, show_hidden:bool=False) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["active"] = self.asBoolean(self.active)
		j["command_id"] = self.asString(self.command_id)
		j["complex"] = self.asBoolean(self.complex)
		j["cooldown"] = self.asInteger(self.cooldown)
		j["cost"] = self.asInteger(self.required_currency)
		j["hidden"] = self.asBoolean(self.hidden)
		j["require"] = self.asInteger(self.require)
		j["trigger"] = self.asString(self.trigger)
		j["uses"] = self.asInteger(self.uses)

		if show_hidden or not self.hidden:
			j["content"] = self.asString(self.content)
			j["description"] = self.asString(self.description)
			j["function"] = self.asString(self.function)
			j["name"] = self.asString(self.name)

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
