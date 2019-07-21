from typing import TYPE_CHECKING, Coroutine, Any
if TYPE_CHECKING:
	from .main_web import PhaazebotWeb

import json
from aiohttp.web import Response, middleware, HTTPException, Request
from Utils.Classes.htmlformatter import HTMLFormatter
from .Processing.Api.errors import apiNotAllowed

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
			if not self.Web.BASE.Active.web:
				return await apiNotAllowed(self, WebRequest, msg="Web is disabled and will be shutdown soon")

			if not self.Web.BASE.Active.api and WebRequest.path.startswith("/api"):
				return await apiNotAllowed(self, WebRequest, msg="API endpoint is not enabled")

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

	# start
	def addRoutes(self) -> None:
		self.addWebRoutes()
		self.addAPIRoutes()

		# favicon
		self.Web.router.add_route('*', '/favicon.ico', self.serveFavicon)

		# unknown path (404)
		self.Web.router.add_route('*', '/{x:.*}', self.notFound)

	# web
	def addWebRoutes(self) -> None:
		# main site
		self.Web.router.add_route('GET', '/', self.mainSite)

		# /admin*
		self.addWebAdminRoutes()

		# /account*
		self.addWebAccountRoutes()

		# /discord*
		self.addWebDiscordRoutes()

		# web contents (js, css, img)
		self.Web.router.add_route('GET', '/img{file:.*}', self.serveImg)
		self.Web.router.add_route('GET', '/css{file:.*}', self.serveCss)
		self.Web.router.add_route('GET', '/js{file:.*}', self.serveJs)

	def addWebAccountRoutes(self) -> None:
		self.Web.router.add_route('GET', '/account', self.accountMain)
		self.Web.router.add_route('GET', '/account/create', self.accountCreate)
		self.Web.router.add_route('GET', '/account/login', self.accountLogin)

	def addWebAdminRoutes(self) -> None:
		self.Web.router.add_route('GET', '/admin', self.adminMain)
		self.Web.router.add_route('GET', '/admin/manage-system', self.adminManageSystem)

	def addWebDiscordRoutes(self) -> None:
		self.Web.router.add_route('GET', '/discord', self.discordMain)
		self.Web.router.add_route('GET', '/discord/login', self.discordLogin)
		self.Web.router.add_route('GET', '/discord/invite', self.discordInvite)
		self.Web.router.add_route('GET', '/discord/dashboard/{guild_id:\d+}', self.discordDashboard)

	# api
	def addAPIRoutes(self) -> None:
		# api/account*
		self.addAPIAccountRoutes()
		# api/admin*
		self.addAPIAdminRoutes()
		# api/admin*
		self.addAPIDiscordRoutes()

		self.Web.router.add_route('*', '/api{x:/?}', self.apiNothing)
		self.Web.router.add_route('*', '/api/{x:.+}', self.apiUnknown)

	def addAPIAccountRoutes(self) -> None:
		self.Web.router.add_route('*', '/api/account/phaaze{x:/?}{method:.*}', self.apiAccountPhaaze)
		self.Web.router.add_route('*', '/api/account/discord{x:/?}{method:.*}', self.apiAccountDiscord)
		self.Web.router.add_route('*', '/api/account/twitch{x:/?}{method:.*}', self.apiAccountTwitch)

	def addAPIAdminRoutes(self) -> None:
		self.Web.router.add_route('*', '/api/admin/module', self.apiAdminModule)
		self.Web.router.add_route('*', '/api/admin/evaluate', self.apiAdminEvaluate)
		self.Web.router.add_route('*', '/api/admin/status', self.apiAdminStatus)

	def addAPIDiscordRoutes(self) -> None:
		self.Web.router.add_route('*', '/api/discord/guilds', self.apiDiscordGuilds)

	# api
	from .Processing.Api.Account.main import apiAccountPhaaze, apiAccountDiscord, apiAccountTwitch
	from .Processing.Api.errors import apiNothing, apiUnknown
	from .Processing.Api.Admin.evaluate import apiAdminEvaluate
	from .Processing.Api.Admin.status import apiAdminStatus
	from .Processing.Api.Admin.module import apiAdminModule
	from .Processing.Api.Discord.servers import apiDiscordGuilds

	# web
	from .Processing.mainsite import mainSite
	from .Processing.Account.accountmain import accountMain
	from .Processing.Account.accountcreate import accountCreate
	from .Processing.Account.accountlogin import accountLogin
	from .Processing.Admin.adminmain import adminMain
	from .Processing.Admin.adminmanagesystem import adminManageSystem
	from .Processing.Discord.discordmain import discordMain
	from .Processing.Discord.discordlogin import discordLogin
	from .Processing.Discord.discorddashboard import discordDashboard
	from .Processing.Discord.discordinvite import discordInvite

	# web contents
	from .Processing.webcontent import serveCss, serveJs, serveImg, serveFavicon

	# errors
	from .Processing.errors import notFound, notAllowed

	# utils
	from .utils import getUserInfo, getDiscordUserInfo
