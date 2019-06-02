from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
	from main import Phaazebot

import json
from aiohttp.web import Request
from Utils.stringutils import password
from Utils.Classes.undefined import Undefined

class WebUserInfo(object):
	"""
		Used for authorisation of a phaaze web user request
		It should if possible, avoid reading in POST content when not needed
	 		variable search way:
			System -> header/cookies -> GET -> POST/JSON
	"""
	def __init__(self, BASE:"Phaazebot", WebRequest:Request, force_method:str=None, **kwargs:Any):
		self.BASE:"Phaazebot" = BASE
		self.WebRequest:Request = WebRequest
		self.kwargs:Any = kwargs
		self.force_method:str = force_method

		self.__session:str = ""
		self.__token:str = ""
		self.__username:str = ""
		self.__password:str = ""

		self.found:bool = False
		self.tryed:bool = False

		self.username:str = None
		self.password:str = None
		self.email:str = None
		self.verified:bool = False
		self.last_login:str = None
		self.user_id:int = None
		self.roles:list = None
		self.role_ids:list = None

	async def auth(self) -> None:
		if self.force_method:
			await getattr(self, self.force_method)()
			return

		await self.getFromSystem()
		if self.tryed: return

		await self.getFromCookies()
		if self.tryed: return
		await self.getFromHeader()
		if self.tryed: return

		await self.getFromGet()
		if self.tryed: return

		# after here we need to read the body
		if self.WebRequest.method in ["POST"]:
			if self.WebRequest.headers.get("content-type", None) == "application/json":
				await self.getFromJson()
				if self.tryed: return

			if self.WebRequest.headers.get("content-type", "").startswith("multipart/"):
				await self.getFromMultipart()
				if self.tryed: return

			await self.getFromPost()
			if self.tryed: return

	# getter
	async def getFromSystem(self) -> None:
		self.__session = self.kwargs.get("phaaze_session", None)
		if self.__session: return await self.viaSession()
		self.__token = self.kwargs.get("phaaze_token", None)
		if self.__session: return await self.via__token()
		self.__username = self.kwargs.get("phaaze_username", None)
		self.__password = self.kwargs.get("phaaze_password", None)
		if self.__password and self.__username: return await self.viaLogin()

	async def getFromCookies(self) -> None:
		self.__session = self.WebRequest.cookies.get("phaaze_session", None)
		if self.__session: return await self.viaSession()
		self.__token = self.WebRequest.cookies.get("phaaze_token", None)
		if self.__session: return await self.via__token()
		# this makes no sense, but ok
		self.__username = self.WebRequest.cookies.get("phaaze_username", None)
		self.__password = self.WebRequest.cookies.get("phaaze_password", None)
		if self.__password and self.__username: return await self.viaLogin()

	async def getFromHeader(self) -> None:
		self.__session = self.WebRequest.headers.get("phaaze_session", None)
		if self.__session: return await self.viaSession()
		self.__token = self.WebRequest.headers.get("phaaze_token", None)
		if self.__session: return await self.via__token()
		# this makes no sense, but ok
		self.__username = self.WebRequest.headers.get("phaaze_username", None)
		self.__password = self.WebRequest.headers.get("phaaze_password", None)
		if self.__password and self.__username: return await self.viaLogin()

	async def getFromGet(self) -> None:
		self.__session = self.WebRequest.query.get("phaaze_session", None)
		if self.__session: return await self.viaSession()
		self.__token = self.WebRequest.query.get("phaaze_token", None)
		if self.__session: return await self.via__token()
		self.__username = self.WebRequest.query.get("phaaze_username", None)
		self.__password = self.WebRequest.query.get("phaaze_password", None)
		if self.__password and self.__username: return await self.viaLogin()

	async def getFromJson(self) -> None:
		try: Json:dict = await self.WebRequest.json()
		except: return

		self.__session = Json.get("phaaze_session", None)
		if self.__session: return await self.viaSession()
		self.__token = Json.get("phaaze_token", None)
		if self.__session: return await self.via__token()
		self.__username = Json.get("phaaze_username", None)
		self.__password = Json.get("phaaze_password", None)
		if self.__password and self.__username: return await self.viaLogin()

	async def getFromMultipart(self) -> None:
		self.BASE.Logger.debug("Someone tryed to auth with multipart content", require="web:debug")
		return None

	async def getFromPost(self) -> None:
		try: Post:dict = await self.WebRequest.post()
		except: return

		self.__session = Post.get("phaaze_session", None)
		if self.__session: return await self.viaSession()
		self.__token = Post.get("phaaze_token", None)
		if self.__session: return await self.via__token()
		self.__username = Post.get("phaaze_username", None)
		self.__password = Post.get("phaaze_password", None)
		if self.__password and self.__username: return await self.viaLogin()

	# checker
	async def viaToken(self) -> None:
		self.BASE.Logger.debug("Someone tryed to auth with token", require="web:debug")
		return None

	async def viaLogin(self) -> None:
		self.__password = password(self.__password)
		dbr:dict = dict(
			of="user",
			store="user",
			where=f"(user['username'] == {json.dumps(self.__username)} or user['email'] == {json.dumps(self.__username)}) and user['password'] == {json.dumps(self.__password)}",
			join=dict(
				of="role",
				store="role",
				where="role['id'] in user['role']",
				fields=["name", "id"]
			)
		)
		return await self.dbRequest(dbr)

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

		self.username = data.get("username", Undefined())
		self.password = data.get("password", Undefined())
		self.email = data.get("email", Undefined())
		self.verified = data.get("verified", Undefined())
		self.last_login = data.get("last_login", Undefined())
		self.user_id = data.get("id", Undefined())
		self.roles = []
		self.role_ids = []
		for role in data.get("role", []):
			self.roles.append( role.get("name", None) )
			self.role_ids.append( role.get("id", None) )
