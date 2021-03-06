from typing import List, Union

from datetime import datetime
from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.contentclass import ContentClass

class WebUser(ContentClass):
	"""
	Contains and represents a phaaze-web user
	"""
	def __init__(self, data:dict):

		self.user_id:int = self.asInteger(data.get("id", UNDEFINED))
		self.username:str = self.asString(data.get("username", UNDEFINED))
		self.username_changed:int = self.asInteger(data.get("username_changed", UNDEFINED))
		self.password:str = self.asString(data.get("password", UNDEFINED))
		self.email:str = self.asString(data.get("email", UNDEFINED))
		self.verified:bool = self.asBoolean(data.get("verified", UNDEFINED))

		self.created_at:datetime = self.asDatetime(data.get("created_at", UNDEFINED))
		self.edited_at:datetime = self.asDatetime(data.get("edited_at", UNDEFINED), allow_null=True)
		self.last_login:datetime = self.asDatetime(data.get("last_login", UNDEFINED), allow_null=True)

		self.roles:List[str] = self.fromStringList(data.get("roles", ''), separator=";;;")

	def __repr__(self):
		return f"<{self.__class__.__name__} id='{self.user_id}' name='{self.username}'>"

	def toJSON(self, dates:bool=True, password:bool=False) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["user_id"] = self.asString(self.user_id)
		j["username"] = self.asString(self.username)
		j["username_changed"] = self.asInteger(self.username_changed)
		j["email"] = self.asString(self.email)
		j["verified"] = self.asBoolean(self.verified)
		j["roles"] = self.asList(self.roles)

		if dates:
			j["created_at"] = self.asString(self.created_at)
			j["edited_at"] = self.asString(self.edited_at)
			j["last_login"] = self.asString(self.last_login)

		if password:
			j["password"] = self.asString(self.password)

		return j

	def checkRoles(self, roles:Union[List[str], str]) -> bool:
		"""
		Checks if a searched roles is assigned to this user
		returns True on first match
		else False
		"""
		if not roles: return True
		if not self.roles: return False
		if type(roles) != list: roles = [roles]

		lower_roles:list = [r.lower() for r in self.roles]

		for role in roles:
			if role.lower() in lower_roles: return True

		return False
