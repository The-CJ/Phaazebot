from typing import TYPE_CHECKING, Any, Callable, Optional, List, Union
if TYPE_CHECKING:
	from main import Phaazebot

import datetime
from aiohttp.web import Request
from multidict import MultiDictProxy
from Utils.stringutils import password as passwordFunction
from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.dbcontentclass import DBContentClass
from Utils.Classes.apiclass import APIClass

def forcible(f:Callable) -> Callable:
	f.__forcible__ = True
	return f

class WebUserInfo(DBContentClass, APIClass):
	"""
	Used for authorisation of a phaaze web user request
	It should if possible, avoid reading in POST content when not needed
	variable search way:
		System -> header/cookies -> GET -> POST/JSON
	"""
	def __init__(self, BASE:"Phaazebot", WebRequest:Optional[Request], force_method:Optional[str]=None, **kwargs):
		self.BASE:"Phaazebot" = BASE
		self.WebRequest:Request = WebRequest
		self.kwargs:Any = kwargs
		self.force_method:str = force_method

		self.__session:str = ""
		self.__token:str = ""
		self.__username:str = ""
		self.__password:str = ""

		self.found:bool = False
		self.tried:bool = False

		self.username:Optional[str] = None
		self.username_changed:int = 0
		self.password:Optional[str] = None
		self.email:Optional[str] = None
		self.verified:bool = False
		self.created_at:Optional[datetime.datetime] = None
		self.edited_at:Optional[datetime.datetime] = None
		self.last_login:Optional[datetime.datetime] = None
		self.user_id:int = -1
		self.roles:List[str] = []

	def __repr__(self):
		if not self.tried and not self.found:
			return f"<{self.__class__.__name__} - Not yet tried to resolve>"

		if not self.found:
			return f"<{self.__class__.__name__} - Not found/Unknown user>"

		return f"<{self.__class__.__name__} id='{self.user_id}' name='{self.username}'>"

	def toJSON(self, dates:bool=True, password:bool=False) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["user_id"] = self.toString(self.user_id)
		j["username"] = self.toString(self.username)
		j["username_changed"] = self.toInteger(self.username_changed)
		j["email"] = self.toString(self.email)
		j["verified"] = self.toBoolean(self.verified)
		j["roles"] = self.toList(self.roles)

		if dates:
			j["created_at"] = self.toString(self.created_at)
			j["edited_at"] = self.toString(self.edited_at)
			j["last_login"] = self.toString(self.last_login)

		if password:
			j["password"] = self.toString(self.password)

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

	async def auth(self) -> None:
		if self.force_method:
			func:Callable = getattr(self, self.force_method)
			if getattr(func, "__forcible__", False):
				return await func()

		await self.getFromSystem()
		if self.tried: return

		await self.getFromCookies()
		if self.tried: return
		await self.getFromHeader()
		if self.tried: return

		await self.getFromGet()
		if self.tried: return

		# after here we need to read the body
		if self.WebRequest.method in ["POST"]:
			if self.WebRequest.headers.get("content-type", "") == "application/json":
				await self.getFromJson()
				if self.tried: return

			if self.WebRequest.headers.get("content-type", "").startswith("multipart/"):
				await self.getFromMultipart()
				if self.tried: return

			await self.getFromPost()
			if self.tried: return

	# getter
	@forcible
	async def getFromSystem(self) -> None:
		self.__session = self.kwargs.get("phaaze_session", None)
		if self.__session: return await self.viaSession()
		self.__username = self.kwargs.get("username", None)
		self.__password = self.kwargs.get("password", None)
		if self.__password and self.__username: return await self.viaLogin()

	@forcible
	async def getFromCookies(self) -> None:
		self.__session = self.WebRequest.cookies.get("phaaze_session", "")
		if self.__session: return await self.viaSession()
		# this makes no sense, but ok
		self.__username = self.WebRequest.cookies.get("username", "")
		self.__password = self.WebRequest.cookies.get("password", "")
		if self.__password and self.__username: return await self.viaLogin()

	@forcible
	async def getFromHeader(self) -> None:
		self.__session = self.WebRequest.headers.get("phaaze_session", "")
		if self.__session: return await self.viaSession()
		# this makes no sense, but ok
		self.__username = self.WebRequest.headers.get("username", "")
		self.__password = self.WebRequest.headers.get("password", "")
		if self.__password and self.__username: return await self.viaLogin()

	@forcible
	async def getFromGet(self) -> None:
		self.__session = self.WebRequest.query.get("phaaze_session", "")
		if self.__session: return await self.viaSession()
		self.__username = self.WebRequest.query.get("username", "")
		self.__password = self.WebRequest.query.get("password", "")
		if self.__password and self.__username: return await self.viaLogin()

	@forcible
	async def getFromJson(self) -> None:
		try: Json:dict = await self.WebRequest.json()
		except: return

		self.__session = Json.get("phaaze_session", None)
		if self.__session: return await self.viaSession()
		self.__username = Json.get("username", None)
		self.__password = Json.get("password", None)
		if self.__password and self.__username: return await self.viaLogin()

	@forcible
	async def getFromMultipart(self) -> None:
		self.BASE.Logger.debug("Someone tried to auth with multipart content", require="web:debug")
		return None

	@forcible
	async def getFromPost(self) -> None:
		try: Post:MultiDictProxy = await self.WebRequest.post()
		except: return

		self.__session = Post.get("phaaze_session", None)
		if self.__session: return await self.viaSession()
		self.__username = Post.get("username", None)
		self.__password = Post.get("password", None)
		if self.__password and self.__username: return await self.viaLogin()

	# checker
	async def viaToken(self) -> None:
		self.BASE.Logger.debug("Someone tried to auth with token", require="web:debug")
		return None

	async def viaLogin(self) -> None:
		self.__password = passwordFunction(self.__password)

		dbr:str = """
			SELECT
				`user`.*,
				GROUP_CONCAT(`role`.`name` SEPARATOR ';;;') AS `roles`
			FROM `user`
			LEFT JOIN `user_has_role`
				ON `user_has_role`.`user_id` = `user`.`id`
			LEFT JOIN `role`
				ON `role`.`id` = `user_has_role`.`role_id`
			WHERE `user`.`password` = %s
				AND (
					`user`.`username` = %s
					OR LOWER(`user`.`email`) = LOWER(%s)
				)
			GROUP BY `user`.`id`"""
		val:tuple = (self.__password, self.__username, self.__username)

		return await self.dbRequest(dbr, val)

	async def viaSession(self) -> None:
		dbr:str = """
			SELECT
				`user`.*,
				GROUP_CONCAT(`role`.`name` SEPARATOR ';;;') AS `roles`
			FROM session_phaaze
			JOIN `user`
				ON `user`.`id` = `session_phaaze`.`user_id`
			LEFT JOIN `user_has_role`
				ON `user_has_role`.`user_id` = `user`.`id`
			LEFT JOIN `role`
				ON `role`.`id` = `user_has_role`.`role_id`
			WHERE `session_phaaze`.`created_at` > (NOW() - INTERVAL 7 DAY)
				AND `session_phaaze`.`session` = %s
			GROUP BY `user`.`id`"""
		val:tuple = (self.__session, )

		return await self.dbRequest(dbr, val)

	async def dbRequest(self, db_req:str, values:tuple = None) -> None:
		self.tried = True
		res:list = self.BASE.PhaazeDB.query(db_req, values=values)

		if not res: return

		await self.finishUser(res[0])

	# finish
	async def finishUser(self, data:dict) -> None:
		self.found = True

		self.user_id = data.get("id", UNDEFINED)
		self.username = data.get("username", UNDEFINED)
		self.username_changed = data.get("username_changed", UNDEFINED)
		self.password = data.get("password", UNDEFINED)
		self.email = data.get("email", UNDEFINED)
		self.verified = bool(data.get("verified", UNDEFINED))

		self.created_at = data.get("created_at", UNDEFINED)
		self.edited_at = data.get("edited_at", UNDEFINED)
		self.last_login = data.get("last_login", UNDEFINED)

		self.roles = self.fromStringList(data.get("roles", ''), ";;;")
