from typing import Any, Callable, Union

import math
from multidict import MultiDictProxy
from aiohttp.web import Request
from Utils.Classes.undefined import Undefined, UNDEFINED

def forcible(f:Callable) -> Callable:
	f.__forcible__ = True
	return f

class WebRequestContent(object):
	"""
	Takes a Request and acts as a central point for variable source,
	same vars from different sources get overwritten.
	Access via X.get(a, b) - if a not found and b is not given,
	it returns Undefined else b

	GET -> POST(multipart/json)

	Reminder:
	---------
	* WebRequestContent.get("aSetValue") -> "a user set value"
	* WebRequestContent.get("aNullOrNoneValue") -> None
	* WebRequestContent.get("aValueNotInRequest") -> UNDEFINED

	Or in Strings:
	--------------
	* WebRequestContent.getStr("newContent", "Alt_Content") -> "Something"
	* WebRequestContent.getStr("aNullField", "Its None") -> "None"
	* WebRequestContent.getStr("aNullField", "Its None", allow_none=True) -> None
	* WebRequestContent.getStr("neverSet", "Missing") -> "Missing"

	"""
	def __init__(self, WebRequest:Request, force_method:str = None):
		self.WebRequest:Request = WebRequest
		self.loaded:bool = False
		self.force_method = force_method
		self.content:dict = dict()

	async def load(self) -> None:
		self.loaded = True
		if self.force_method:
			func:Callable = getattr(self, self.force_method)
			if getattr(func, "__forcible__", False):
				return await func()

		await self.unpackGet()

		if self.WebRequest.method in ["POST", "PATCH", "DELETE"]:
			content_type:str = self.WebRequest.headers.get("content-type", "")
			if content_type == "application/json":
				await self.unpackJson()

			elif content_type.startswith("multipart/"):
				await self.unpackMultipart()

			else:
				await self.unpackPost()

	@forcible
	async def unpackGet(self) -> None:
		self.content = {**self.content, **self.WebRequest.query}

	@forcible
	async def unpackPost(self) -> None:
		Post:MultiDictProxy = await self.WebRequest.post()
		self.content = {**self.content, **Post}

	@forcible
	async def unpackJson(self) -> None:
		try:
			json_content:dict = await self.WebRequest.json()
			self.content = {**self.content, **json_content}
		except:
			pass

	@forcible
	async def unpackMultipart(self) -> None:
		return None

	def get(self, a:str, b:Any = UNDEFINED) -> Any:
		"""
		get any value from the stored content
		"""
		if not self.loaded: raise RuntimeError("Content not loaded, call 'await X.load()' before")
		return self.content.get(a, b)

	def getBool(self, x:str, alternative:Any, allow_none:bool = False) -> Union[bool, Any, None]:
		"""
		get a value as bool.
		False = "0", "false", "False", ""
		True = Everything else
		"""
		value:Any = self.get(x)

		if allow_none and value is None:
			return None

		if type(value) is Undefined:
			return alternative

		if value in ["0", "false", "False", ""]:
			return False
		else:
			return True

	def getStr(self, x:str, alternative:Any, len_min:int = -math.inf, len_max:int = math.inf, must_be_digit:bool = False, strip:bool = True, allow_none:bool = False) -> Union[str, Any, None]:
		"""
		get a value as string.
		test: does it only contains digits, it its to short or to long,
		if one fails, return alternative

		by default, strip's spaces + line breaks at start and end
		"""
		value:Any = self.get(x)

		if allow_none and value is None:
			return None

		if type(value) is Undefined:
			return alternative

		value:str = str(value)

		if strip: value = value.strip(' ').strip("\n")

		if must_be_digit and not value.isdigit():
			return alternative

		if not (len_min <= len(value) <= len_max):
			return alternative

		return value

	def getInt(self, x:str, alternative:Any, min_x:int = -math.inf, max_x:int = math.inf, allow_none:bool = False) -> Union[int, Any]:
		"""
		get a value as a int.
		if conversion is not possible
		or the found value is not in min <= X <= max
		return alternative
		"""
		value:Any = self.get(x)

		if allow_none and value is None:
			return None

		if type(value) is Undefined:
			return alternative

		try:
			value:int = int(value)
			if min_x <= value <= max_x:
				return value
			else:
				return alternative
		except:
			return alternative
