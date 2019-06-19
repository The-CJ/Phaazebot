from typing import TYPE_CHECKING, Any, Callable
if TYPE_CHECKING:
	pass

from aiohttp.web import Request
from .undefined import Undefined

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
		self.success:bool = False
		self.method:str = None
		self.force_method = force_method
		self.content:dict = dict()

	async def load(self) -> None:
		if self.force_method:
			func:Callable = getattr(self, self.force_method)
			if getattr(func, "__forcable__", False):
				return await func()

		await self.unpackGet()

		if self.WebRequest.method in ["POST"]:
			if self.WebRequest.headers.get("content-type", None) == "application/json":
				await self.unpackJson()

			elif self.WebRequest.headers.get("content-type", "").startswith("multipart/"):
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
		json_content:dict = await self.WebRequest.post()
		self.content = {**self.content, **json_content}

	@forcable
	async def unpackMultipart(self) -> None:
		self.BASE.Logger.debug("Someone send data via multipart content", require="web:debug")
		return None

	def get(self, a:str, b:Any = Undefined()) -> Any:
		return self.__content.get(a, b)
