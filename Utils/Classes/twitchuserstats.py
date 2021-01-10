from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Twitch.main_twitch import PhaazebotTwitch

from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.contentclass import ContentClass
from Utils.Classes.apiclass import APIClass

class TwitchUserStats(ContentClass, APIClass):
	"""
	Contains and represents all phaaze values for a Twitch user
	"""
	def __init__(self, data:dict):

		# key
		self.channel_id:str = data.get("channel_id", UNDEFINED)
		self.user_id:str = data.get("user_id", UNDEFINED)

		# vars
		self.active:int = data.get("active", UNDEFINED)
		self.amount_currency:int = int( data.get("exp", 0) )
		self.amount_time:int = int( data.get("currency", 0) )

		# calc
		self.rank:int = data.get("rank", UNDEFINED)
		self.edited:bool = bool( data.get("edited", False) )
		self.regular:bool = bool( data.get("regular", False) )

	def __repr__(self):
		return f"<{self.__class__.__name__} channel='{self.channel_id}' user='{self.user_id}'>"

	async def editCurrency(self, cls:"PhaazebotTwitch", amount_by:int=None, amount_to:int=None) -> None:

		if amount_by and amount_to: raise AttributeError("'amount_by' and 'amount_to' can't both be given")

		sql:str = "UPDATE `twitch_user`"
		values:tuple = ()

		if amount_by != None:
			sql += " SET `amount_currency` = `amount_currency` + %s"
			values += ( int(amount_by) )

		if amount_to != None:
			sql += " SET `amount_currency` = %s"
			values += ( int(amount_to) )

		sql += " WHERE `channel_id` = %s AND `user_id` = %s"
		values += ( str(self.channel_id), str(self.user_id) )

		cls.BASE.PhaazeDB.query(sql, values)
		cls.BASE.Logger.debug(f"(Twitch) Updated currency: {self.channel_id=} {self.user_id=}", require="twitch:level")

	def toJSON(self, include_active:bool=False) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["channel_id"] = self.toString(self.channel_id)
		j["user_id"] = self.toString(self.user_id)
		j["amount_currency"] = self.toInteger(self.amount_currency)
		j["amount_time"] = self.toInteger(self.amount_time)
		j["rank"] = self.toList(self.rank)
		j["edited"] = self.toBoolean(self.edited)
		j["regular"] = self.toBoolean(self.regular)

		if include_active:
			j["active"] = self.toInteger(self.active)

		return j
