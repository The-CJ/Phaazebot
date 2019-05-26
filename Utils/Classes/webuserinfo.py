from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
	from main import Phaazebot

from aiohttp.web import Request

class WebUserInfo(object):
	"""
		Used for authorisation of a web user request
		It should if possible, avoid reading in POST content when not needed
	 		variable search way:
			System -> header/cookies -> GET -> POST/JSON
	"""
	def __init__(self, BASE:"Phaazebot", WebRequest:Request, **kwargs:Any):
		self.BASE:"Phaazebot" = BASE
		self.WebRequest:Request = WebRequest
		self.kwargs:Any = kwargs

		self.__session:str = ""
		self.__token:str = ""
		self.__username:str = ""
		self.__password:str = ""

		self.found:bool = False
		self.tryed:bool = False

		self.role:list = list()
		self.role_ids:list = list()

	async def auth(self) -> None:
		await self.getFromSystem()
		if self.tryed: return

		await self.getFromCookies()
		if self.tryed: return
		await self.getFromHeader()
		if self.tryed: return

		await self.getFromGet()
		if self.tryed: return

		# after here we need to read the body
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
		if self.__session: return self.viaSession()
		self.__token = self.kwargs.get("phaaze___token", None)
		if self.__session: return self.via__token()
		self.__username = self.kwargs.get("phaaze___username", None)
		self.__password = self.kwargs.get("phaaze___password", None)
		if self.__password and self.__username: return self.viaLogin()

	async def getFromCookies(self) -> None:
		self.__session = self.WebRequest.cookies.get("phaaze_session", None)
		if self.__session: return self.viaSession()
		self.__token = self.WebRequest.cookies.get("phaaze___token", None)
		if self.__session: return self.via__token()
		# this makes no sense, but ok
		self.__username = self.WebRequest.cookies.get("phaaze___username", None)
		self.__password = self.WebRequest.cookies.get("phaaze___password", None)
		if self.__password and self.__username: return self.viaLogin()

	async def getFromHeader(self) -> None:
		self.__session = self.WebRequest.headers.get("phaaze_session", None)
		if self.__session: return self.viaSession()
		self.__token = self.WebRequest.headers.get("phaaze___token", None)
		if self.__session: return self.via__token()
		# this makes no sense, but ok
		self.__username = self.WebRequest.headers.get("phaaze___username", None)
		self.__password = self.WebRequest.headers.get("phaaze___password", None)
		if self.__password and self.__username: return self.viaLogin()

	async def getFromGet(self) -> None:
		self.__session = self.WebRequest.query.get("phaaze_session", None)
		if self.__session: return self.viaSession()
		self.__token = self.WebRequest.query.get("phaaze___token", None)
		if self.__session: return self.via__token()
		self.__username = self.WebRequest.query.get("phaaze___username", None)
		self.__password = self.WebRequest.query.get("phaaze___password", None)
		if self.__password and self.__username: return self.viaLogin()

	async def getFromJson(self) -> None:
		try: Json:dict = await self.WebRequest.json()
		except: return

		self.__session = Json.get("phaaze_session", None)
		if self.__session: return self.viaSession()
		self.__token = Json.get("phaaze___token", None)
		if self.__session: return self.via__token()
		self.__username = Json.get("phaaze___username", None)
		self.__password = Json.get("phaaze___password", None)
		if self.__password and self.__username: return self.viaLogin()

	async def getFromMultipart(self) -> None:
		self.BASE.Logger.debug("Someone tryed to auth with multipart content", require="web:debug")
		return None

	async def getFromPost(self) -> None:
		try: Post:dict = await self.WebRequest.post()
		except: return

		self.__session = Post.get("phaaze_session", None)
		if self.__session: return self.viaSession()
		self.__token = Post.get("phaaze___token", None)
		if self.__session: return self.via__token()
		self.__username = Post.get("phaaze___username", None)
		self.__password = Post.get("phaaze___password", None)
		if self.__password and self.__username: return self.viaLogin()

	# checker
	async def viatoken(self) -> None:
		pass

	async def viaLogin(self) -> None:
		pass

	async def viaSession(self) -> None:
		pass

	# finish
	async def finishUser(self) -> None:
		pass
