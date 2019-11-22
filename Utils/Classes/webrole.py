from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.dbcontentclass import DBContentClass

class WebRole(DBContentClass):
	"""
		Contains and represents a role for the web server
	"""
	def __repr__(self):
		return f"<{self.__class__.__name__} id='{self.guild_id}' name='{self.role_id}'>"

	def __init__(self, data:dict):
		self.id:str = data.get("id", UNDEFINED)
		self.name:str = data.get("name", UNDEFINED)
		self.description:str = data.get("description", UNDEFINED)
		self.can_be_removed:bool = bool( data.get("can_be_removed", UNDEFINED) )
