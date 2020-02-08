from typing import TYPE_CHECKING, Any, Callable
if TYPE_CHECKING:
	pass

import math
from aiohttp.web import Request
from .undefined import Undefined, UNDEFINED

def forcable(f:Callable) -> Callable:
	f.__forcable__ = True
	return f

class WebRequestContent(object):
	"""
		Takes a Request and acts as a central point for variable source,
		same vars from different sourcees get overwritten.
		Access via X.get(a, b) - if a not found and b is not given,
		it returnes Undefined else b

		GET -> POST(multipart/json)
	"""
	def __init__(self, WebRequest:Request, force_method:str=None):
		self.WebRequest:Request = WebRequest
		self.loaded:bool = False
		self.force_method = force_method
		self.content:dict = dict()

	async def load(self) -> None:
		self.loaded = True
		if self.force_method:
			func:Callable = getattr(self, self.force_method)
			if getattr(func, "__forcable__", False):
				return await func()

		await self.unpackGet()

		if self.WebRequest.method in ["POST"]:
			content_type:str = self.WebRequest.headers.get("content-type", "")
			if content_type == "application/json":
				await self.unpackJson()

			elif content_type.startswith("multipart/"):
				await self.unpackMultipart()

			else:
				await self.unpackPost()

	@forcable
	async def unpackGet(self) -> None:
		self.content = {**self.content, **self.WebRequest.query}

	@forcable
	async def unpackPost(self) -> None:
		post_content:dict = await self.WebRequest.post()
		self.content = {**self.content, **post_content}

	@forcable
	async def unpackJson(self) -> None:
		try:
			json_content:dict = await self.WebRequest.json()
			self.content = {**self.content, **json_content}
		except:
			pass

	@forcable
	async def unpackMultipart(self) -> None:
		self.BASE.Logger.debug("Someone send data via multipart content", require="web:debug")
		return None

	def get(self, a:str, b:Any = UNDEFINED) -> Any:
		"""
			get any value from the stored content
		"""
		if not self.loaded: raise RuntimeError("Content not loaded, call 'await X.load()' before")
		return self.content.get(a, b)

	def getBool(self, x:str, alternativ:bool) -> bool:
		"""
			get a value as bool.
			Flase = "0", "false", "False", ""
			True = Everything else
		"""
		value:str or Undefined = self.get(x)
		if type(value) is Undefined: return alternativ

		if value in ["0", "false", "False", ""]: return False
		else: return True

	def getStr(self, x:str, alternativ:str, must_be_digit:bool=False, strip:bool=True) -> str:
		"""
			get a value as string.
			test for attributes (must_*), if one failes, return alternativ

			by default, strip's spaces + line breaks at start and end
		"""
		value:str or Undefined = self.get(x)
		if type(value) is Undefined: return alternativ

		if must_be_digit and not value.isdigit(): return alternativ

		if strip: value = value.strip(' ').strip("\n")

		return value

	def getInt(self, x:str, alternativ:int, min_x:int=-math.inf, max_x:int=math.inf) -> int:
		"""
			get a value as a int.
			if convertion is not possible
			or the found value is not in min <= X <= max
			return alternativ
		"""

		value:str or Undefined = self.get(x)
		if type(value) is Undefined: return alternativ

		try:
			value:int = int(value)
			if min_x <= value <= max_x:
				return value
			else:
				return alternativ
		except:
			return alternativ
