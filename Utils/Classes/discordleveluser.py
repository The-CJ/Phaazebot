from Utils.Classes.undefined import Undefined

class DiscordLevelUser(object):
	"""
		Contains and represents all level values for a Discord user
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} server='{self.server_id}' member='{self.member_id}'>"

	def __init__(self, data:dict, server_id:str):

		self.server_id:str = server_id
		self.member_id:str = data.get("member_id", Undefined())
		self.exp:int = data.get("exp", 0)
		self.edited:bool = data.get("edited", False)
		self.medals:str = data.get("medals", Undefined())
