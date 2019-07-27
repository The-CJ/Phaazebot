from Utils.Classes.undefined import Undefined
from Utils.Classes.dbcontentclass import DBContentClass

class DiscordLevelUser(DBContentClass):
	"""
		Contains and represents all level values for a Discord user
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} server='{self.server_id}' member='{self.member_id}'>"

	def __init__(self, data:dict, server_id:str):

		self.server_id:str = str( server_id )
		self.member_id:str = str( data.get("member_id", Undefined()) )
		self.exp:int = int( data.get("exp", 0) )
		self.edited:bool = bool( data.get("edited", False) )
		self.medals:str = self.fromJsonFiel( data.get("medals", Undefined()) )
