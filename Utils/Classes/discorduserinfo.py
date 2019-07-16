from typing import TYPE_CHECKING, Any, Callable
if TYPE_CHECKING:
	from main import Phaazebot

import json
from aiohttp.web import Request

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
			of="session/phaaze",
			store="session",
			where=f'session["session"] == {json.dumps(self.__session)}',
			limit=1,
			join=dict(
				of="user",
				store="user",
				where="session['user_id'] == user['id']",
				join=dict(
					of="role",
					store="role",
					where="role['id'] in user['role']",
					fields=["name", "id"]
				)
			)
		)
		return await self.dbRequest(dbr, unpack_session = True)

	async def dbRequest(self, db_req:dict, unpack_session:bool = False) -> None:
		self.tryed = True
		res:dict = self.BASE.PhaazeDB.select(**db_req)

		if int(res.get("hits", 0)) != 1:
			return

		if unpack_session:
			await self.finishUser(res["data"][0]["user"][0])
		else:
			await self.finishUser(res["data"][0])

	# finish
	async def finishUser(self, data:dict) -> None:
		self.found = True
