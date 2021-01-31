from typing import TYPE_CHECKING, Callable, Optional, List
if TYPE_CHECKING:
	from phaazebot import Phaazebot

from multidict import MultiDictProxy
from Utils.stringutils import passwordToHash as passwordFunction
from Utils.Classes.extendedrequest import ExtendedRequest
from Utils.Classes.webuser import WebUser
from Platforms.Web.db import getWebUsers

def forcible(f:Callable) -> Callable:
	f.__forcible__ = True
	return f

class AuthWebUser(object):
	"""
	Used for authorisation of a phaaze web user request.
	When `found` is True, `User` will contain a valid WebUser
	It should if possible, avoid reading in POST content when not needed
	variable search way:

	* System -> cookies -> header -> GET -> JSON -> POST
	"""
	def __init__(self, BASE:"Phaazebot", WebRequest:ExtendedRequest, force_method:Optional[str]=None, **kwargs):
		self.BASE:"Phaazebot" = BASE
		self.WebRequest:ExtendedRequest = WebRequest
		self.force_method:str = force_method
		self.User:Optional[WebUser] = None

		# name holder
		self.field_session:str = "phaaze_session"
		self.field_username:str = "phaaze_username"
		self.field_password:str = "phaaze_password"

		# internal arguments
		self.__kwargs:dict = kwargs
		self.__session:str = ""
		self.__token:str = ""
		self.__username:str = ""
		self.__password:str = ""

		self.found:bool = False
		self.tried:bool = False

	def __repr__(self):
		if not self.tried and not self.found:
			return f"<{self.__class__.__name__} - Not yet tried to resolve>"

		if not self.found:
			return f"<{self.__class__.__name__} - Not found/Unknown user>"

		return f"<{self.__class__.__name__} id='{self.User.user_id}' name='{self.User.username}'>"

	async def auth(self) -> None:
		if self.force_method:
			func:Callable = getattr(self, self.force_method)
			if getattr(func, "__forcible__", False):
				return await func()

		await self.viaSystem()
		if self.tried: return

		await self.viaCookies()
		if self.tried: return

		await self.viaHeader()
		if self.tried: return

		await self.viaGet()
		if self.tried: return

		# after here we need to read the body
		if self.WebRequest.method in ["POST"]:
			if self.WebRequest.headers.get("content-type", "") == "application/json":
				await self.viaJson()
				if self.tried: return

			if self.WebRequest.headers.get("content-type", "").startswith("multipart/"):
				await self.viaMultipart()
				if self.tried: return

			await self.viaPost()
			if self.tried: return

	# getter
	@forcible
	async def viaSystem(self) -> None:
		self.__session = self.__kwargs.get(self.field_session, "")
		if self.__session:
			return await self.authSession()

		self.__username = self.__kwargs.get(self.field_username, "")
		self.__password = self.__kwargs.get(self.field_password, "")
		if self.__password and self.__username:
			return await self.authCredentials()

	@forcible
	async def viaCookies(self) -> None:
		self.__session = self.WebRequest.cookies.get(self.field_session, "")
		if self.__session:
			return await self.authSession()

		# this makes no sense, but ok
		self.__username = self.WebRequest.cookies.get(self.field_username, "")
		self.__password = self.WebRequest.cookies.get(self.field_password, "")
		if self.__password and self.__username:
			return await self.authCredentials()

	@forcible
	async def viaHeader(self) -> None:
		self.__session = self.WebRequest.headers.get(self.field_session, "")
		if self.__session:
			return await self.authSession()

		# this makes no sense, but ok
		self.__username = self.WebRequest.headers.get(self.field_username, "")
		self.__password = self.WebRequest.headers.get(self.field_password, "")
		if self.__password and self.__username:
			return await self.authCredentials()

	@forcible
	async def viaGet(self) -> None:
		self.__session = self.WebRequest.query.get(self.field_session, "")
		if self.__session:
			return await self.authSession()

		self.__username = self.WebRequest.query.get(self.field_username, "")
		self.__password = self.WebRequest.query.get(self.field_password, "")
		if self.__password and self.__username:
			return await self.authCredentials()

	@forcible
	async def viaJson(self) -> None:
		try: Json:dict = await self.WebRequest.json()
		except: return

		self.__session = Json.get(self.field_session, "")
		if self.__session:
			return await self.authSession()

		self.__username = Json.get(self.field_username, "")
		self.__password = Json.get(self.field_password, "")
		if self.__password and self.__username:
			return await self.authCredentials()

	@forcible
	async def viaMultipart(self) -> None:
		self.BASE.Logger.debug("Someone tried to auth with multipart content", require="web:debug")
		return None

	@forcible
	async def viaPost(self) -> None:
		try: Post:MultiDictProxy = await self.WebRequest.post()
		except: return

		self.__session = Post.get(self.field_session, "")
		if self.__session:
			return await self.authSession()

		self.__username = Post.get(self.field_username, "")
		self.__password = Post.get(self.field_password, "")
		if self.__password and self.__username:
			return await self.authCredentials()

	# auths
	async def authToken(self) -> None:
		self.BASE.Logger.debug("Someone tried to auth with token", require="web:debug")
		return None

	async def authCredentials(self) -> None:
		self.tried = True
		self.__password = passwordFunction(self.__password)

		sql:str = """
			SELECT `user`.`id` as `user_id`
			FROM `user`
			WHERE `user`.`password` = %s
				AND ( 1=2
					OR LOWER(`user`.`username`) = LOWER(%s)
					OR LOWER(`user`.`email`) = LOWER(%s)
				)
			LIMIT 1"""
		val:tuple = (self.__password, self.__username, self.__username)

		user_id_res:List[dict] = self.BASE.PhaazeDB.selectQuery(sql, val)

		if user_id_res:
			user_id:int = user_id_res[0]["user_id"]
			user_res:List[WebUser] = await getWebUsers(self.BASE.Web, user_id=user_id)
			if user_res:
				self.found = True
				self.User = user_res.pop(0)

	async def authSession(self) -> None:
		self.tried = True

		sql:str = """
			SELECT `session_phaaze`.`user_id` AS `user_id`
			FROM `session_phaaze`
			WHERE `session_phaaze`.`session` = %s
			LIMIT 1"""
		val:tuple = (self.__session, )

		user_id_res:List[dict] = self.BASE.PhaazeDB.selectQuery(sql, val)
		if user_id_res:
			user_id:int = user_id_res[0]["user_id"]
			user_res:List[WebUser] = await getWebUsers(self.BASE.Web, user_id=user_id)
			if user_res:
				self.found = True
				self.User = user_res.pop(0)