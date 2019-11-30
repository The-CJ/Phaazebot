from Utils.Classes.undefined import Undefined
from Utils.Classes.dbcontentclass import DBContentClass

class DiscordLevelUser(DBContentClass):
	"""
		Contains and represents all level values for a Discord user
	"""
	def __init__(self, data:dict, server_id:str):

		self.server_id:str = server_id
		self.member_id:str = data.get("member_id", Undefined())
		self.rank:int = data.get("rank", Undefined())
		self.exp:int = int( data.get("exp", 0) )
		self.edited:bool = bool( data.get("edited", False) )
		self.medals:list = self.fromStringList( data.get("medals", Undefined() ), ";;;" )

	def __repr__(self):
		return f"<{self.__class__.__name__} server='{self.server_id}' member='{self.member_id}'>"

	def toJSON(self) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["member_id"] = self.member_id
		j["rank"] = self.rank
		j["exp"] = self.exp
		j["edited"] = bool(self.edited)
		j["medals"] = self.medals

		return j
