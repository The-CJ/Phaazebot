from Utils.Classes.undefined import Undefined
from Utils.Classes.dbcontentclass import DBContentClass

class DiscordQuote(DBContentClass):
	"""
		Contains and represents stuff for a discord quote
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} server='{self.guild_id}' quote='{self.quote_id}'>"

	def __init__(self, data:dict, guild_id:str):

		self.guild_id:str = guild_id
		self.quote_id:str = data.get("id", Undefined())
		self.content:str = data.get("content", Undefined())
