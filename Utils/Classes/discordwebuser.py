from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.contentclass import ContentClass

class DiscordWebUser(ContentClass):
	"""
	Contains information's about a discord web user,
	this object is suppose to be appended to a `AuthDiscordWebUser` object.

	It contains data similar to discord.User,
	but its actually only filled with data we got from discord when the user authorised pha aze access.
	"""
	def __init__(self, data:dict):
		self.user_id:str = self.asString(data.get("id", UNDEFINED))
		self.username:str = self.asString(data.get("username", UNDEFINED))
		self.email:str = self.asString(data.get("email", UNDEFINED))
		self.verified:bool = self.asBoolean(data.get("verified", UNDEFINED))
		self.locale:str = self.asString(data.get("locale", UNDEFINED))
		self.premium_type:int = self.asInteger(data.get("premium_type", UNDEFINED))
		self.flags:int = self.asInteger(data.get("flags", UNDEFINED))
		self.avatar:str = self.asString(data.get("avatar", UNDEFINED))
		self.discriminator:str = self.asString(data.get("discriminator", UNDEFINED))

	def __repr__(self):
		return f"<{self.__class__.__name__} id='{self.user_id}' name='{self.username}'>"

	def toJSON(self) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["user_id"] = self.asString(self.user_id)
		j["username"] = self.asString(self.username)
		j["email"] = self.asString(self.email)
		j["verified"] = self.asBoolean(self.verified)
		j["locale"] = self.asString(self.locale)
		j["premium_type"] = self.asInteger(self.premium_type)
		j["flags"] = self.asInteger(self.flags)
		j["avatar"] = self.asString(self.avatar)
		j["discriminator"] = self.asString(self.discriminator)

		return j
