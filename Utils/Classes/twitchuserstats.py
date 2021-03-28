from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
	from Platforms.Twitch.main_twitch import PhaazebotTwitch

from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.contentclass import ContentClass

class TwitchUserStats(ContentClass):
	"""
	Contains and represents all phaaze values for a Twitch user
	"""
	def __init__(self, data:dict):

		# key
		self.channel_id:str = self.asString(data.get("channel_id", UNDEFINED))
		self.user_id:str = self.asString(data.get("user_id", UNDEFINED))

		# vars
		self.active:int = self.asInteger(data.get("active", UNDEFINED))
		self.edited:bool = self.asBoolean(data.get("edited", False))
		self.amount_currency:int = self.asInteger(data.get("exp", UNDEFINED))
		self.amount_time:int = self.asInteger(data.get("currency", UNDEFINED))

		# calc
		self.rank:int = self.asInteger(data.get("rank", UNDEFINED))
		self.regular:bool = self.asBoolean(data.get("regular", False))

	def __repr__(self):
		return f"<{self.__class__.__name__} channel='{self.channel_id}' user='{self.user_id}'>"

	async def editCurrency(self, cls:"PhaazebotTwitch", amount_by:Optional[int]=None, amount_to:Optional[int]=None) -> None:

		if amount_by and amount_to: raise AttributeError("'amount_by' and 'amount_to' can't both be given")

		sql:str = "UPDATE `twitch_user`"
		values:tuple = ()

		if amount_by is not None:
			sql += " SET `amount_currency` = `amount_currency` + %s"
			values += (amount_by,)

		if amount_to is not None:
			sql += " SET `amount_currency` = %s"
			values += (amount_to,)

		sql += " WHERE `channel_id` = %s AND `user_id` = %s"
		values += (self.channel_id, self.user_id)

		cls.BASE.PhaazeDB.query(sql, values)
		cls.BASE.Logger.debug(f"(Twitch) Updated currency: {self.channel_id=} {self.user_id=}", require="twitch:level")

	def toJSON(self, include_active:bool=False) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["channel_id"] = self.asString(self.channel_id)
		j["user_id"] = self.asString(self.user_id)
		j["amount_currency"] = self.asInteger(self.amount_currency)
		j["amount_time"] = self.asInteger(self.amount_time)
		j["rank"] = self.asInteger(self.rank)
		j["edited"] = self.asBoolean(self.edited)
		j["regular"] = self.asBoolean(self.regular)

		if include_active:
			j["active"] = self.asInteger(self.active)

		return j
