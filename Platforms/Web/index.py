from typing import TYPE_CHECKING, Coroutine, Any
if TYPE_CHECKING:
	from .main_web import PhaazebotWeb

import json
from aiohttp.web import Response, middleware, HTTPException, Request
from Platforms.Web.utils import HTMLFormatter

class WebIndex(object):
	""" Contains all functions for the web to call """
	def __init__(self, Web:"PhaazebotWeb"):
		self.Web:"PhaazebotWeb" = Web
		self.Web.middlewares.append(self.middleware_handler)
		self.HTMLRoot:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/root.html", template=True)

	def response(self, status:int=200, content_type:str=None, body:Any=None, **kwargs:Any) -> Response:
		already_set_header:dict = kwargs.get('headers', dict())
		kwargs['headers'] = already_set_header
		kwargs['headers']['server'] =f"PhaazeOS v{self.Web.BASE.version}"

		return Response(status=status, content_type=content_type, body=body, **kwargs)

	@middleware
	async def middleware_handler(self, Request:Request, handler:Coroutine) -> Response:
		try:
			response:Response = await handler(Request)
			return response

		except HTTPException as HTTPEx:
			return self.response(
				body=json.dumps( dict(msg=HTTPEx.reason, status=HTTPEx.status) ),
				status=HTTPEx.status,
				content_type='application/json'
			)
		except Exception as e:
			self.Web.BASE.Logger.error(f"(Web) Error in request {str(e)}")
			return self.response(
				status=500,
				body=json.dumps( dict(msg=str(e), status=500) ),
				content_type='application/json'
			)

	def addRoutes(self) -> None:

		# web contents (js, css, img)
		self.Web.router.add_route('GET', '/img{file:.*}', self.serveImg)
		self.Web.router.add_route('GET', '/css{file:.*}', self.serveCss)
		self.Web.router.add_route('GET', '/js{file:.*}', self.serveJs)

		# unknown path (404)
		self.Web.router.add_route('*', '/{x:.*}', self.notFound)

	# utils

	# web contents
	from .Processing.webcontent import (serveCss, serveJs, serveImg)

	# errors
	from .Processing.errors import notFound