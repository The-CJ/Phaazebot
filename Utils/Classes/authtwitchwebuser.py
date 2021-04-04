from typing import TYPE_CHECKING, Callable, Optional, List
if TYPE_CHECKING:
	from phaazebot import Phaazebot

import json
from datetime import datetime
from aiohttp.web import Request
from Utils.Classes.contentclass import ContentClass
from Utils.Classes.twitchuser import TwitchUser
from Utils.Classes.undefined import UNDEFINED

def forcible(f:Callable) -> Callable:
	f.__forcible__ = True
	return f

class AuthTwitchWebUser(ContentClass):
	"""
	Used for authorisation of a twitch web user request
	variable search way:
		System -> cookies -> header -> GET
	"""
	def __init__(self, BASE:"Phaazebot", WebRequest:Request, force_method:Optional[str]=None, **kwargs):
		self.BASE:"Phaazebot" = BASE
		self.WebRequest:Request = WebRequest
		self.force_method:str = force_method
		self.User:Optional[TwitchUser] = None

		# name holder
		self.field_session:str = "phaaze_twitch_session"

		# special session values
		self.access_token:Optional[str] = None
		self.refresh_token:Optional[str] = None
		self.scope:Optional[str] = None
		self.token_type:Optional[str] = None
		self.created_at:Optional[datetime] = None

		# internal arguments
		self.__kwargs:dict = kwargs
		self.__session:str = ""

		self.found:bool = False
		self.tried:bool = False

	def __repr__(self):
		if not self.tried and not self.found:
			return f"<{self.__class__.__name__} - Not yet tried to resolve>"

		if not self.found:
			return f"<{self.__class__.__name__} - Not found/Unknown user>"

		return f"<{self.__class__.__name__} id='{self.User.user_id}' login='{self.User.login}'>"

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

	# getter
	@forcible
	async def viaSystem(self) -> None:
		self.__session = self.__kwargs.get(self.field_session, "")
		if self.__session:
			return await self.authSession()

	@forcible
	async def viaCookies(self) -> None:
		self.__session = self.WebRequest.cookies.get(self.field_session, "")
		if self.__session:
			return await self.authSession()

	@forcible
	async def viaHeader(self) -> None:
		self.__session = self.WebRequest.headers.get(self.field_session, "")
		if self.__session:
			return await self.authSession()

	@forcible
	async def viaGet(self) -> None:
		self.__session = self.WebRequest.query.get(self.field_session, "")
		if self.__session:
			return await self.authSession()

	async def authSession(self) -> None:
		self.tried = True

		sql:str = """
			SELECT `session_twitch`.*
			FROM `session_twitch`
			WHERE `session_twitch`.`session` = %s
				AND `session_twitch`.`created_at` > (NOW() - INTERVAL 7 DAY)
			LIMIT 1"""
		val:tuple = (self.__session,)

		info_res:List[dict] = self.BASE.PhaazeDB.selectQuery(sql, val)
		if info_res:
			info:dict = info_res.pop()

			self.found = True

			# extract special session values
			self.access_token = self.asString(info.get("access_token", UNDEFINED))
			self.refresh_token = self.asString(info.get("refresh_token", UNDEFINED))
			self.scope = self.asString(info.get("scope", UNDEFINED))
			self.token_type = self.asString(info.get("token_type", UNDEFINED))
			self.created_at = self.asDatetime(info.get("created_at", UNDEFINED))

			user_info: dict = json.loads(info.get("user_info", "{}"))
			self.User = TwitchUser(user_info)

	def toJSON(self, images:bool=True, types:bool=False, token:bool=False, scope:bool=False) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		if self.User is not None:
			j.update(self.User.toJSON(images=images, types=types))

		if token:
			j["access_token"] = self.asString(self.access_token)
			j["refresh_token"] = self.asString(self.refresh_token)

		if scope:
			j["scope"] = self.asString(self.scope)

		return j
