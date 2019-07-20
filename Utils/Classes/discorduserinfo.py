from typing import TYPE_CHECKING, Any, Callable
if TYPE_CHECKING:
	from main import Phaazebot

import json
from aiohttp.web import Request
from Utils.Classes.undefined import Undefined

def forcable(f:Callable) -> Callable:
	f.__forcable__ = True
	return f

class DiscordUserInfo(object):
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

		self.username:str = None
		self.verified:str = None
		self.locale:str = None
		self.premium_type:str = None
		self.user_id:str = None
		self.flags:str = None
		self.avatar:str = None
		self.discriminator:str = None
		self.email:str = None

		self.found:bool = False
		self.tryed:bool = False

	async def auth(self) -> None:
		if self.force_method:
			func:Callable = getattr(self, self.force_method)
			if getattr(func, "__forcable__", False):
				return await func()

		await self.getFromSystem()
		if self.tryed: return

		await self.getFromCookies()
		if self.tryed: return
		await self.getFromHeader()
		if self.tryed: return

		await self.getFromGet()
		if self.tryed: return

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
		dbr:dict = dict(
			of="session/discord",
			store="session",
			where=f'session["session"] == {json.dumps(self.__session)}',
			limit=1,
		)
		return await self.dbRequest(dbr)

	async def dbRequest(self, db_req:dict) -> None:
		self.tryed = True
		res:dict = self.BASE.PhaazeDB.select(**db_req)

		if int(res.get("hits", 0)) != 1:
			return

		await self.finishUser(res["data"][0])

	# finish
	async def finishUser(self, data:dict) -> None:
		self.found = True

		self.access_token:str = data.get("access_token", Undefined())
		self.refresh_token:str = data.get("refresh_token", Undefined())
		self.scope:str = data.get("scope", Undefined())

		user:dict = data.get("user_info", dict())

		self.username:str = user.get("username", Undefined())
		self.verified:str = user.get("verified", Undefined())
		self.locale:str = user.get("locale", Undefined())
		self.premium_type:str = user.get("premium_type", Undefined())
		self.user_id:str = user.get("id", Undefined())
		self.flags:str = user.get("flags", Undefined())
		self.avatar:str = user.get("avatar", Undefined())
		self.discriminator:str = user.get("discriminator", Undefined())
		self.email:str = user.get("email", Undefined())
