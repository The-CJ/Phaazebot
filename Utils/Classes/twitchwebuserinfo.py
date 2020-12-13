from typing import TYPE_CHECKING, Any, Callable
if TYPE_CHECKING:
	from main import Phaazebot

import json
from aiohttp.web import Request
from Utils.Classes.undefined import UNDEFINED
from Utils.Classes.dbcontentclass import DBContentClass
from Utils.Classes.apiclass import APIClass

def forcable(f:Callable) -> Callable:
	f.__forcable__ = True
	return f

class TwitchWebUserInfo(DBContentClass, APIClass):
	"""
	Used for authorisation of a twitch web user request
	(Don't get confused with `TwitchUser` object, these objects are used for general twitch api results)
	(TwitchWebUserInfo is only used for a info storage for the current request twitch user)
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
		self.name:str = None
		self.display_name:str = None
		self.user_type:str = None
		self.broadcaster_type:str = None
		self.description:str = None
		self.profile_image_url:str = None
		self.offline_image_url:str = None
		self.view_count:int = None
		self.email:str = False

		self.found:bool = False
		self.tried:bool = False

	def __repr__(self):
		if not self.tried and not self.found:
			return f"<{self.__class__.__name__} - Not yet tried to resolve>"

		if not self.found:
			return f"<{self.__class__.__name__} - Not found/Unknown user>"

		return f"<{self.__class__.__name__} id='{self.user_id}' name='{self.username}'>"

	def toJSON(self, images:bool=True, types:bool=False, token:bool=False, scope:bool=False) -> dict:
		""" Returns a json save dict representation of all values for API, storage, etc... """

		j:dict = dict()

		j["user_id"] = self.toString(self.user_id)
		j["name"] = self.toString(self.name)
		j["display_name"] = self.toString(self.display_name)
		j["description"] = self.toString(self.description)
		j["view_count"] = self.toInteger(self.view_count)
		j["email"] = self.toString(self.email)

		if images:
			j["profile_image_url"] = self.toString(self.profile_image_url)
			j["offline_image_url"] = self.toString(self.offline_image_url)

		if types:
			j["user_type"] = self.toString(self.user_type)
			j["broadcaster_type"] = self.toString(self.broadcaster_type)

		if token:
			j["access_token"] = self.toString(self.access_token)
			j["refresh_token"] = self.toString(self.refresh_token)

		if scope:
			j["scope"] = self.toString(self.scope)

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
		self.__session = self.kwargs.get("phaaze_twitch_session", None)
		if self.__session: return await self.viaSession()

	@forcable
	async def getFromCookies(self) -> None:
		self.__session = self.WebRequest.cookies.get("phaaze_twitch_session", None)
		if self.__session: return await self.viaSession()

	@forcable
	async def getFromHeader(self) -> None:
		self.__session = self.WebRequest.headers.get("phaaze_twitch_session", None)
		if self.__session: return await self.viaSession()

	@forcable
	async def getFromGet(self) -> None:
		self.__session = self.WebRequest.query.get("phaaze_twitch_session", None)
		if self.__session: return await self.viaSession()

	async def viaSession(self) -> None:
		dbr:str = """
			SELECT * FROM `session_twitch`
			WHERE `session_twitch`.`created_at` > (NOW() - INTERVAL 7 DAY)
				AND `session_twitch`.`session` = %s"""

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

		self.user_id:str = user.get("user_id", UNDEFINED)
		self.name:str = user.get("name", UNDEFINED)
		self.display_name:str = user.get("display_name", UNDEFINED)
		self.description:str = user.get("description", UNDEFINED)
		self.view_count:int = user.get("view_count", 0)
		self.email:str = user.get("email", UNDEFINED)
		self.user_type:str = user.get("user_type", UNDEFINED)
		self.broadcaster_type:str = user.get("broadcaster_type", UNDEFINED)
		self.profile_image_url:str = user.get("profile_image_url", UNDEFINED)
		self.offline_image_url:str = user.get("offline_image_url", UNDEFINED)
