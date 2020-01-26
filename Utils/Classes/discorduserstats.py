from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.dbcontentclass import DBContentClass

class DiscordUserStats(DBContentClass):
	"""
		Contains and represents all phaaze values for a Discord user
	"""
	def __init__(self, data:dict, server_id:str):

		self.server_id:str = server_id
		self.member_id:str = data.get("member_id", UNDEFINED)
		self.rank:int = int( data.get("rank", UNDEFINED) )
		self.exp:int = int( data.get("exp", 0) )
		self.currency:int = int( data.get("currency", 0) )
		self.edited:bool = bool( data.get("edited", False) )
		self.medals:list = self.fromStringList( data.get("medals", UNDEFINED ), ";;;" )

	def __repr__(self):
		return f"<{self.__class__.__name__} server='{self.server_id}' member='{self.member_id}'>"

	async def editCurrency(self, cls:"PhaazebotDiscord", amount:int) -> None:
		cls.BASE.PhaazeDB.query("""
			UPDATE `discord_user`
			SET `currency` = `currency` + %s
			WHERE `guild_id` = %s AND `member_id` = %s""",
			(amount, self.server_id, self.member_id)
		)

		cls.BASE.Logger.debug(f"(Discord) Updated currency: S:{self.server_id} U:{self.member_id}", require="discord:command")

	def toJSON(self) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["member_id"] = str(self.member_id)
		j["rank"] = int(self.rank)
		j["exp"] = int(self.exp)
		j["currency"] = int(self.currency)
		j["edited"] = bool(self.edited)
		j["medals"] = list(self.medals)

		return j
