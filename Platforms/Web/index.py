from typing import TYPE_CHECKING, Coroutine, Any
if TYPE_CHECKING:
	from .main_web import PhaazebotWeb

import re
import json
from aiohttp.web import Response, middleware, HTTPException, Request

class WebIndex(object):
	""" Contains all functions for the web to call """
	def __init__(self, Web:"PhaazebotWeb"):
		self.Web:"PhaazebotWeb" = Web
		self.FormatHTMLRegex:re.Pattern = re.compile(r"\|>>>\((.+?)\)<<<\|")
		self.Web.router.add_route("*", "/{x:.*}", self.test)

	def response(self, status:int=200, content_type:str=None, body:Any=None, **kwargs:Any) -> Response:
		already_set_header:dict = kwargs.get('headers', dict())
		kwargs['headers'] = already_set_header
		kwargs['headers']['server'] =f"PhaazeOS v{self.Web.BASE.version}"

		return Response(status=status, content_type=content_type, body=body, **kwargs)

	@middleware
	async def middleware_handler(self, Request:Request, handler:Coroutine) -> None:
		try:
			response = await handler(Request)
			return response

		except HTTPException as HTTPEx:
			return self.response(
				body=json.dumps( dict(msg=HTTPEx.reason, status=HTTPEx.status) ),
				status=HTTPEx.status,
				content_type='application/json'
			)
		except Exception as e:
			self.Web.BASE.Logger.error(str(e))

	async def test(self, Request:Request):
		print(f"{str(self)} - {str(self.Web)} - {str(Request)}")
		return self.response(status=200, content_type="text/html", body="TODO")
