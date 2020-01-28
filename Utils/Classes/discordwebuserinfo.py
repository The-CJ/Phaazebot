from typing import TYPE_CHECKING, Any, Callable
if TYPE_CHECKING:
	from main import Phaazebot

import json
from aiohttp.web import Request
from Utils.Classes.undefined import UNDEFINED

def forcable(f:Callable) -> Callable:
	f.__forcable__ = True
	return f

class DiscordWebUserInfo(object):
	"""
		Used for authorisation of a discord web user request
		variable search way:
			System -> header/cookies
	"""
	def __init__(self, BASE:"Phaazebot", WebRequest:Request, force_method:str=None, **kwargs:Any):
		self.BASE:"Phaazebot" = BASE
		self.WebRequest:Request = WebRequest
		self.kwargs:Any = kwargs
		self.force_method:str = force_method

		self.__session:str = ""

		self.access_token:str = None
		self.refresh_token:str = None
		self.scope:str = None

		self.user_id:str = None
		self.username:str = None
		self.email:str = None
		self.verified:bool = False
		self.locale:str = None
		self.premium_type:int = None
		self.flags:int = None
		self.avatar:str = None
		self.discriminator:str = None

		self.found:bool = False
		self.tried:bool = False

	def __repr__(self):
		if not self.tried and not self.found:
			return f"<{self.__class__.__name__} - Not yet tried to resolve>"

		if not self.found:
			return f"<{self.__class__.__name__} - Not found/Unknown user>"

		return f"<{self.__class__.__name__} id='{self.user_id}' name='{self.username}'>"

	def toJSON(self, token:bool=False, scope:bool=False) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["user_id"] = str(self.user_id)
		j["username"] = self.username
		j["email"] = self.email
		j["verified"] = self.verified
		j["locale"] = self.locale
		j["premium_type"] = self.premium_type
		j["flags"] = self.flags
		j["avatar"] = self.avatar
		j["discriminator"] = self.discriminator

		if token:
			j["access_token"] = self.access_token
			j["refresh_token"] = self.refresh_token

		if scope:
			j["scope"] = self.scope

		return j

	async def auth(self) -> None:
		if self.force_method:
			func:Callable = getattr(self, self.force_method)
			if getattr(func, "__forcable__", False):
				return await func()

		await self.getFromSystem()
		if self.tried: return

		await self.getFromCookies()
		if self.tried: return
		await self.getFromHeader()
		if self.tried: return

		await self.getFromGet()
		if self.tried: return

	# getter
	@forcable
	async def getFromSystem(self) -> None:
		self.__session = self.kwargs.get("phaaze_discord_session", None)
		if self.__session: return await self.viaSession()

	@forcable
	async def getFromCookies(self) -> None:
		self.__session = self.WebRequest.cookies.get("phaaze_discord_session", None)
		if self.__session: return await self.viaSession()

	@forcable
	async def getFromHeader(self) -> None:
		self.__session = self.WebRequest.headers.get("phaaze_discord_session", None)
		if self.__session: return await self.viaSession()

	@forcable
	async def getFromGet(self) -> None:
		self.__session = self.WebRequest.query.get("phaaze_discord_session", None)
		if self.__session: return await self.viaSession()

	async def viaSession(self) -> None:
		dbr:str = """
			SELECT * FROM `session_discord`
			WHERE `session_discord`.`created_at` > (NOW() - INTERVAL 7 DAY)
				AND `session_discord`.`session` = %s"""

		val:tuple = (self.__session,)
		return await self.dbRequest(dbr, val)

	async def dbRequest(self, db_req:str, values:tuple = None) -> None:
		self.tried = True
		res:list = self.BASE.PhaazeDB.query(db_req, values=values)

		if not res: return

		await self.finishUser(res[0])

	# finish
	async def finishUser(self, data:dict) -> None:
		self.found = True

		self.access_token:str = data.get("access_token", UNDEFINED)
		self.refresh_token:str = data.get("refresh_token", UNDEFINED)
		self.scope:str = data.get("scope", UNDEFINED)

		user:dict = json.loads(data.get("user_info", "{}"))

		self.username = user.get("username", UNDEFINED)
		self.verified = user.get("verified", UNDEFINED)
		self.locale = user.get("locale", UNDEFINED)
		self.premium_type = user.get("premium_type", UNDEFINED)
		self.user_id = user.get("id", UNDEFINED)
		self.flags = user.get("flags", UNDEFINED)
		self.avatar = user.get("avatar", UNDEFINED)
		self.discriminator = user.get("discriminator", UNDEFINED)
		self.email = user.get("email", UNDEFINED)
