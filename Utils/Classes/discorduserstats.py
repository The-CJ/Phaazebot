from typing import TYPE_CHECKING, Optional, List
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.contentclass import ContentClass
from Utils.Classes.discordusermedal import DiscordUserMedal

class DiscordUserStats(ContentClass):
	"""
	Contains and represents all phaaze values for a Discord user
	"""
	def __init__(self, data:dict):

		# key
		self.guild_id:str = self.asString(data.get("guild_id", UNDEFINED))
		self.member_id:str = self.asString(data.get("member_id", UNDEFINED))

		# vars
		self.currency:int = self.asInteger(data.get("currency", 0))
		self.edited:bool = self.asBoolean(data.get("edited", False))
		self.exp:int = self.asInteger(data.get("exp", 0))
		self.nickname:str = self.asString(data.get("nickname", UNDEFINED))
		self.on_server:bool = self.asBoolean(data.get("on_server", UNDEFINED))
		self.username:str = self.asString(data.get("username", UNDEFINED))

		# calc
		self.rank:int = self.asInteger(data.get("rank", UNDEFINED))
		self.regular:bool = self.asBoolean(data.get("regular", False))
		self.medals:list = self.fromStringList(data.get("medals", UNDEFINED), separator=";;;")

	def __repr__(self):
		return f"<{self.__class__.__name__} server='{self.server_id}' member='{self.member_id}'>"

	async def editCurrency(self, cls:"PhaazebotDiscord", amount_by:Optional[int]=None, amount_to:Optional[int]=None) -> None:

		if amount_by and amount_to: raise AttributeError("'amount_by' and 'amount_to' can't both be given")

		sql:str = "UPDATE `discord_user`"
		values:tuple = ()

		if amount_by is not None:
			sql += " SET `currency` = `currency` + %s"
			values += (amount_by,)

		if amount_to is not None:
			sql += " SET `currency` = %s"
			values += (amount_to,)

		sql += " WHERE `guild_id` = %s AND `member_id` = %s"
		values += (self.guild_id, self.member_id)

		cls.BASE.PhaazeDB.query(sql, values)
		cls.BASE.Logger.debug(f"(Discord) Updated currency: S:{self.server_id} U:{self.member_id}", require="discord:command")

	def toJSON(self) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["guild_id"] = self.asString(self.guild_id)
		j["member_id"] = self.asString(self.member_id)
		j["currency"] = self.asInteger(self.currency)
		j["edited"] = self.asBoolean(self.edited)
		j["exp"] = self.asInteger(self.exp)
		j["nickname"] = self.asString(self.nickname)
		j["on_server"] = self.asInteger(self.on_server)
		j["username"] = self.asString(self.username)
		j["rank"] = self.asInteger(self.rank)
		j["regular"] = self.asBoolean(self.regular)
		j["medals"] = self.asList(self.medals)

		return j

	async def getMedals(self, cls:"PhaazebotDiscord") -> List[DiscordUserMedal]:
		"""
		Get associated medals of this user
		"""
		from Platforms.Discord.db import getDiscordUsersMedals
		search:dict = {
			"member_id": self.member_id,
			"guild_id": self.guild_id,
		}
		return await getDiscordUsersMedals(cls, **search)

	@property
	def server_id(self) -> str:
		return self.guild_id
