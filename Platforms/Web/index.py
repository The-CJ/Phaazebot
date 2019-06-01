from typing import TYPE_CHECKING, Coroutine, Any
if TYPE_CHECKING:
	from .main_web import PhaazebotWeb

import json
from aiohttp.web import Response, middleware, HTTPException, Request
from Utils.Classes.htmlformatter import HTMLFormatter

class WebIndex(object):
	""" Contains all functions for the web to call """
	def __init__(self, Web:"PhaazebotWeb"):
		self.Web:"PhaazebotWeb" = Web
		self.Web.middlewares.append(self.middlewareHandler)
		self.HTMLRoot:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/root.html", template=True)

	def response(self, status:int=200, content_type:str=None, **kwargs:Any) -> Response:
		already_set_header:dict = kwargs.get('headers', dict())
		kwargs['headers'] = already_set_header
		kwargs['headers']['server'] =f"PhaazeOS v{self.Web.BASE.version}"

		return Response(status=status, content_type=content_type, **kwargs)

	@middleware
	async def middlewareHandler(self, WebRequest:Request, handler:Coroutine) -> Response:
		try:
			response:Response = await handler(WebRequest)
			return response

		except HTTPException as HTTPEx:
			return self.response(
				body=json.dumps( dict(msg=HTTPEx.reason, status=HTTPEx.status) ),
				status=HTTPEx.status,
				content_type='application/json'
			)
		except Exception as e:
			self.Web.BASE.Logger.error(f"(Web) Error in request: {str(e)}")
			return self.response(
				status=500,
				body=json.dumps( dict(msg=str(e), status=500) ),
				content_type='application/json'
			)

	def addRoutes(self) -> None:
		self.addWebRoutes()
		self.addAPIRoutes()

		# favicon
		self.Web.router.add_route('*', '/favicon.ico', self.serveFavicon)

		# unknown path (404)
		self.Web.router.add_route('*', '/{x:.*}', self.notFound)

	def addWebRoutes(self) -> None:
		# main site
		self.Web.router.add_route('GET', '/', self.mainSite)

		# /account*
		self.addWebAccountRoutes()

		# web contents (js, css, img)
		self.Web.router.add_route('GET', '/img{file:.*}', self.serveImg)
		self.Web.router.add_route('GET', '/css{file:.*}', self.serveCss)
		self.Web.router.add_route('GET', '/js{file:.*}', self.serveJs)

	def addWebAccountRoutes(self) -> None:
		self.Web.router.add_route('GET', '/account', self.accountMain)
		self.Web.router.add_route('GET', '/account/create', self.accountCreate)

	def addAPIRoutes(self) -> None:
		self.addAPIAccountroutes()

		self.Web.router.add_route('*', '/api{x:/?}', self.apiNothing)
		self.Web.router.add_route('*', '/api/{x:.+}', self.apiUnknown)

	def addAPIAccountroutes(self) -> None:
		self.Web.router.add_route('*', '/api/account/phaaze{x:/?}{method:.*}', self.apiAccountPhaaze)
		self.Web.router.add_route('*', '/api/account/discord{x:/?}{method:.*}', self.apiAccountDiscord)
		self.Web.router.add_route('*', '/api/account/twitch{x:/?}{method:.*}', self.apiAccountTwitch)

	# api
	from .Processing.Api.errors import apiNothing, apiUnknown

	# api/account
	from .Processing.Api.account import apiAccountPhaaze, apiAccountDiscord, apiAccountTwitch

	# web
	from .Processing.mainsite import mainSite
	from .Processing.Account.accountmain import accountMain
	from .Processing.Account.accountcreate import accountCreate

	# web contents
	from .Processing.webcontent import (serveCss, serveJs, serveImg, serveFavicon)

	# errors
	from .Processing.errors import notFound

	# utils
	from .utils import getUserInfo
