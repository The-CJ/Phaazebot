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

		self.session:str = ""
		self.token:str = ""
		self.username:str = ""
		self.password:str = ""

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
		self.session = self.kwargs.get("phaaze_session", None)
		if self.session: return self.viaSession()
		self.token = self.kwargs.get("phaaze_token", None)
		if self.session: return self.viaToken()
		self.username = self.kwargs.get("phaaze_username", None)
		self.password = self.kwargs.get("phaaze_password", None)
		if self.password and self.username: return self.viaLogin()

	async def getFromCookies(self) -> None:
		self.session = self.WebRequest.cookies.get("phaaze_session", None)
		if self.session: return self.viaSession()
		self.token = self.WebRequest.cookies.get("phaaze_token", None)
		if self.session: return self.viaToken()
		# this makes no sense, but ok
		self.username = self.WebRequest.cookies.get("phaaze_username", None)
		self.password = self.WebRequest.cookies.get("phaaze_password", None)
		if self.password and self.username: return self.viaLogin()

	async def getFromHeader(self) -> None:
		self.session = self.WebRequest.headers.get("phaaze_session", None)
		if self.session: return self.viaSession()
		self.token = self.WebRequest.headers.get("phaaze_token", None)
		if self.session: return self.viaToken()
		# this makes no sense, but ok
		self.username = self.WebRequest.headers.get("phaaze_username", None)
		self.password = self.WebRequest.headers.get("phaaze_password", None)
		if self.password and self.username: return self.viaLogin()

	async def getFromGet(self) -> None:
		self.session = self.WebRequest.query.get("phaaze_session", None)
		if self.session: return self.viaSession()
		self.token = self.WebRequest.query.get("phaaze_token", None)
		if self.session: return self.viaToken()
		self.username = self.WebRequest.query.get("phaaze_username", None)
		self.password = self.WebRequest.query.get("phaaze_password", None)
		if self.password and self.username: return self.viaLogin()

	async def getFromJson(self) -> None:
		try: Json:dict = await self.WebRequest.json()
		except: return

		self.session = Json.get("phaaze_session", None)
		if self.session: return self.viaSession()
		self.token = Json.get("phaaze_token", None)
		if self.session: return self.viaToken()
		self.username = Json.get("phaaze_username", None)
		self.password = Json.get("phaaze_password", None)
		if self.password and self.username: return self.viaLogin()

	async def getFromMultipart(self) -> None:
		self.BASE.Logger.debug("Someone tryed to auth with multipart content", require="web:debug")
		return None

	async def getFromPost(self) -> None:
		try: Post:dict = await self.WebRequest.post()
		except: return

		self.session = Post.get("phaaze_session", None)
		if self.session: return self.viaSession()
		self.token = Post.get("phaaze_token", None)
		if self.session: return self.viaToken()
		self.username = Post.get("phaaze_username", None)
		self.password = Post.get("phaaze_password", None)
		if self.password and self.username: return self.viaLogin()

	# checker
	async def viaToken(self) -> None:
		pass

	async def viaLogin(self) -> None:
		pass

	async def viaSession(self) -> None:
		pass

	# finish
	async def finishUser(self) -> None:
		pass
