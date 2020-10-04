from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Discord.main_discord import PhaazebotDiscord

from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.dbcontentclass import DBContentClass
from Utils.Classes.apiclass import APIClass

class DiscordUserStats(DBContentClass, APIClass):
	"""
	Contains and represents all phaaze values for a Discord user
	"""
	def __init__(self, data:dict, server_id:str):

		# key
		self.guild_id:str = server_id # don't ask
		self.server_id:str = server_id # don't ask
		self.member_id:str = data.get("member_id", UNDEFINED)

		# vars
		self.currency:int = int( data.get("currency", 0) )
		self.edited:bool = bool( data.get("edited", False) )
		self.exp:int = int( data.get("exp", 0) )
		self.nickname:str = data.get("nickname", UNDEFINED)
		self.on_server:bool = bool( data.get("on_server", UNDEFINED) )
		self.username:str = data.get("username", UNDEFINED)

		# calc
		self.rank:int = int( data.get("rank", UNDEFINED) )
		self.regular:bool = bool( data.get("regular", False) )
		self.medals:list = self.fromStringList( data.get("medals", UNDEFINED ), ";;;" )

	def __repr__(self):
		return f"<{self.__class__.__name__} server='{self.server_id}' member='{self.member_id}'>"

	async def editCurrency(self, cls:"PhaazebotDiscord", amount_by:int=None, amount_to:int=None) -> None:

		if amount_by and amount_to: raise AttributeError("'amount_by' and 'amount_to' can't both be given")

		sql:str = "UPDATE `discord_user`"
		values:tuple = ()

		if amount_by != None:
			sql += " SET `currency` = `currency` + %s"
			values += ( int(amount_by) )

		if amount_to != None:
			sql += " SET `currency` = %s"
			values += ( int(amount_to) )

		sql += " WHERE `guild_id` = %s AND `member_id` = %s"
		values += ( str(self.guild_id), str(self.member_id) )

		cls.BASE.PhaazeDB.query(sql, values)
		cls.BASE.Logger.debug(f"(Discord) Updated currency: S:{self.server_id} U:{self.member_id}", require="discord:command")

	def toJSON(self) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["guild_id"] = self.toString(self.guild_id)
		j["member_id"] = self.toString(self.member_id)
		j["currency"] = self.toInteger(self.currency)
		j["edited"] = self.toBoolean(self.edited)
		j["exp"] = self.toInteger(self.exp)
		j["nickname"] = self.toString(self.nickname)
		j["on_server"] = self.toInteger(self.on_server)
		j["username"] = self.toString(self.username)
		j["rank"] = self.toInteger(self.rank)
		j["regular"] = self.toBoolean(self.regular)
		j["medals"] = self.toList(self.medals)

		return j
