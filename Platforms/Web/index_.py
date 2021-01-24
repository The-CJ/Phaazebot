from typing import TYPE_CHECKING, Callable
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

import json
import traceback
from aiohttp.web import Response, middleware, HTTPException, Request
from Utils.cli import CliArgs
from Utils.Classes.htmlformatter import HTMLFormatter

# entry points | api
from Platforms.Web.Processing.Api.Account.main import apiAccountPhaaze, apiAccountDiscord, apiAccountTwitch

# entry points | api admin
from Platforms.Web.Processing.Api.Admin.evaluate import apiAdminEvaluate
from Platforms.Web.Processing.Api.Admin.status import apiAdminStatus
from Platforms.Web.Processing.Api.Admin.module import apiAdminModule
from Platforms.Web.Processing.Api.Admin.avatar import apiAdminAvatar
from Platforms.Web.Processing.Api.Admin.Roles.main import apiAdminRoles
from Platforms.Web.Processing.Api.Admin.Users.main import apiAdminUsers

# entry points | api discord
from Platforms.Web.Processing.Api.Discord.guild import apiDiscordGuild
from Platforms.Web.Processing.Api.Discord.userguilds import apiDiscordUserGuilds
from Platforms.Web.Processing.Api.Discord.Commands.main import apiDiscordCommands
from Platforms.Web.Processing.Api.Discord.search import apiDiscordSearch
from Platforms.Web.Processing.Api.Discord.Configs.Regulardisabledchannels.main import apiDiscordConfigsRegularDisabledChannels
from Platforms.Web.Processing.Api.Discord.Configs.Normaldisabledchannels.main import apiDiscordConfigsNormalDisabledChannels
from Platforms.Web.Processing.Api.Discord.Configs.Leveldisabledchannels.main import apiDiscordConfigsLevelDisabledChannels
from Platforms.Web.Processing.Api.Discord.Configs.Quotedisabledchannels.main import apiDiscordConfigsQuoteDisabledChannels
from Platforms.Web.Processing.Api.Discord.Configs.Gameenabledchannels.main import apiDiscordConfigsGameEnabledChannels
from Platforms.Web.Processing.Api.Discord.Configs.Nsfwenabledchannels.main import apiDiscordConfigsNsfwEnabledChannels
from Platforms.Web.Processing.Api.Discord.Configs.Blacklistedwords.main import apiDiscordConfigsBlacklistedWords
from Platforms.Web.Processing.Api.Discord.Configs.Whitelistedlinks.main import apiDiscordConfigsWhitelistedLink
from Platforms.Web.Processing.Api.Discord.Configs.Exceptionroles.main import apiDiscordConfigsExceptionRoles
from Platforms.Web.Processing.Api.Discord.Levels.Medals.main import apiDiscordLevelsMedals
from Platforms.Web.Processing.Api.Discord.Configs.main import apiDiscordConfigs
from Platforms.Web.Processing.Api.Discord.Levels.main import apiDiscordLevels
from Platforms.Web.Processing.Api.Discord.Regulars.main import apiDiscordRegulars
from Platforms.Web.Processing.Api.Discord.Quotes.main import apiDiscordQuotes
from Platforms.Web.Processing.Api.Discord.Assignroles.main import apiDiscordAssignroles
from Platforms.Web.Processing.Api.Discord.Twitchalerts.main import apiDiscordTwitchalerts
from Platforms.Web.Processing.Api.Discord.Logs.main import apiDiscordLogs

# entry points | web
from Platforms.Web.Processing.mainsite import mainSite
from Platforms.Web.Processing.Account.accountmain import accountMain
from Platforms.Web.Processing.Account.accountcreate import accountCreate
from Platforms.Web.Processing.Account.accountlogin import accountLogin

# entry points | web admin
from Platforms.Web.Processing.Admin.adminmain import adminMain
from Platforms.Web.Processing.Admin.adminmanagesystem import adminManageSystem
from Platforms.Web.Processing.Admin.adminmanagerole import adminManageRole
from Platforms.Web.Processing.Admin.adminmanageuser import adminManageUser

# entry points | web discord
from Platforms.Web.Processing.Discord.discordmain import discordMain
from Platforms.Web.Processing.Discord.discordlogin import discordLogin
from Platforms.Web.Processing.Discord.discordquotes import discordQuotes
from Platforms.Web.Processing.Discord.discordview import discordView
from Platforms.Web.Processing.Discord.discorddashboard import discordDashboard
from Platforms.Web.Processing.Discord.discordinvite import discordInvite
from Platforms.Web.Processing.Discord.discordcommands import discordCommands
from Platforms.Web.Processing.Discord.discordlevels import discordLevels

# entry points | web contents
from Platforms.Web.Processing.webcontent import serveCss, serveJs, serveImg
from Platforms.Web.Processing.webcontent import serveFavicon

# entry points | errors
from Platforms.Web.Processing.errors import notFound, notAllowed, underDev

# entry points | api errors
from Platforms.Web.Processing.Api.errors import apiNotAllowed
from Platforms.Web.Processing.Api.errors import apiNothing, apiUnknown

# entry points | utils
from Platforms.Web.utils import getWebUserInfo, getDiscordUserInfo, getTwitchUserInfo

class WebIndex(object):
	""" Contains all functions for the web to call """
	def __init__(self, Web:"PhaazebotWeb"):
		self.Web:"PhaazebotWeb" = Web
		self.Web.middlewares.append(self.middlewareHandler)
		self.HTMLRoot:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/root.html", template=True)

	def response(self, status:int=200, content_type:str="text/plain", **kwargs) -> Response:
		already_set_header:dict = kwargs.get('headers', {})
		kwargs['headers'] = already_set_header
		kwargs['headers']['server'] = f"PhaazeOS v{self.Web.BASE.version}"

		return Response(status=status, content_type=content_type, **kwargs)

	@middleware
	async def middlewareHandler(self, WebRequest:Request, handler:Callable) -> Response:
		try:
			if not self.Web.BASE.Active.web:
				return await apiNotAllowed(self, WebRequest, msg="Web is disabled and will be shutdown soon")

			if not self.Web.BASE.Active.api and WebRequest.path.startswith("/api"):
				return await apiNotAllowed(self, WebRequest, msg="API endpoint is not enabled")

			response:Response = await handler(WebRequest)
			return response

		except HTTPException as HTTPEx:
			return self.response(
				body=json.dumps(dict(msg=HTTPEx.reason, status=HTTPEx.status)),
				status=HTTPEx.status,
				content_type='application/json'
			)
		except Exception as e:
			tb:str = traceback.format_exc()
			self.Web.BASE.Logger.error(f"(Web) Error in request: {str(e)}\n{tb}")
			error:str = str(e) if CliArgs.get("debug") == "all" else "Unknown error"
			return self.response(
				status=500,
				body=json.dumps(dict(msg=error, status=500)),
				content_type='application/json'
			)

	# start
	def addRoutes(self) -> None:
		self.addWebRoutes()
		self.addAPIRoutes()

		# unknown path (404)
		self.Web.router.add_route('*', '/{x:.*}', self.notFound)

	# web
	def addWebRoutes(self) -> None:
		# /admin*
		self.addWebAdminRoutes()

		# /account*
		self.addWebAccountRoutes()

		# /discord*
		self.addWebDiscordRoutes()

		# temporal added routs due to dev
		self.Web.router.add_route('GET', '/twitch{x:.*}', self.underDev)
		self.Web.router.add_route('GET', '/osu{x:.*}', self.underDev)
		self.Web.router.add_route('GET', '/wiki{x:.*}', self.underDev)
		self.Web.router.add_route('GET', '/bug{x:.*}', self.underDev)

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
		self.Web.router.add_route('GET', '/admin/manage-role', self.adminManageRole)
		self.Web.router.add_route('GET', '/admin/manage-user', self.adminManageUser)

	def addWebDiscordRoutes(self) -> None:
		self.Web.router.add_route('GET', '/discord', self.discordMain)
		self.Web.router.add_route('GET', '/discord/login', self.discordLogin)
		self.Web.router.add_route('GET', '/discord/invite', self.discordInvite)
		self.Web.router.add_route('GET', '/discord/commands/{guild_id:\d+}', self.discordCommands)
		self.Web.router.add_route('GET', '/discord/quotes/{guild_id:\d+}', self.discordQuotes)
		self.Web.router.add_route('GET', '/discord/levels/{guild_id:\d+}', self.discordLevels)
		self.Web.router.add_route('GET', '/discord/dashboard/{guild_id:\d+}', self.discordDashboard)
		self.Web.router.add_route('GET', '/discord/view/{guild_id:\d+}', self.discordView)

	# api
	def addAPIRoutes(self) -> None:
		# api/account*
		self.addAPIAccountRoutes()
		# api/admin*
		self.addAPIAdminRoutes()
		# api/discord*
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
		self.Web.router.add_route('*', '/api/admin/avatar', self.apiAdminAvatar)
		self.Web.router.add_route('*', '/api/admin/roles{x:/?}{method:.*}', self.apiAdminRoles)
		self.Web.router.add_route('*', '/api/admin/users{x:/?}{method:.*}', self.apiAdminUsers)

	def addAPIDiscordRoutes(self) -> None:
		self.Web.router.add_route('*', '/api/discord/guild', self.apiDiscordGuild)
		self.Web.router.add_route('*', '/api/discord/userguilds', self.apiDiscordUserGuilds)
		self.Web.router.add_route('*', '/api/discord/search', self.apiDiscordSearch)
		self.Web.router.add_route('*', '/api/discord/commands{x:/?}{method:.*}', self.apiDiscordCommands)
		self.Web.router.add_route('*', '/api/discord/configs/regulardisabledchannels{x:/?}{method:.*}', self.apiDiscordConfigsRegularDisabledChannels)
		self.Web.router.add_route('*', '/api/discord/configs/normaldisabledchannels{x:/?}{method:.*}', self.apiDiscordConfigsNormalDisabledChannels)
		self.Web.router.add_route('*', '/api/discord/configs/leveldisabledchannels{x:/?}{method:.*}', self.apiDiscordConfigsLevelDisabledChannels)
		self.Web.router.add_route('*', '/api/discord/configs/quotedisabledchannels{x:/?}{method:.*}', self.apiDiscordConfigsQuoteDisabledChannels)
		self.Web.router.add_route('*', '/api/discord/configs/gameenabledchannels{x:/?}{method:.*}', self.apiDiscordConfigsGameEnabledChannels)
		self.Web.router.add_route('*', '/api/discord/configs/nsfwenabledchannels{x:/?}{method:.*}', self.apiDiscordConfigsNsfwEnabledChannels)
		self.Web.router.add_route('*', '/api/discord/configs/blacklistedwords{x:/?}{method:.*}', self.apiDiscordConfigsBlacklistedWords)
		self.Web.router.add_route('*', '/api/discord/configs/whitelistedlinks{x:/?}{method:.*}', self.apiDiscordConfigsWhitelistedLink)
		self.Web.router.add_route('*', '/api/discord/configs/exceptionroles{x:/?}{method:.*}', self.apiDiscordConfigsExceptionRoles)
		self.Web.router.add_route('*', '/api/discord/configs{x:/?}{method:.*}', self.apiDiscordConfigs)
		self.Web.router.add_route('*', '/api/discord/levels/medals{x:/?}{method:.*}', self.apiDiscordLevelsMedals)
		self.Web.router.add_route('*', '/api/discord/levels{x:/?}{method:.*}', self.apiDiscordLevels)
		self.Web.router.add_route('*', '/api/discord/regulars{x:/?}{method:.*}', self.apiDiscordRegulars)
		self.Web.router.add_route('*', '/api/discord/quotes{x:/?}{method:.*}', self.apiDiscordQuotes)
		self.Web.router.add_route('*', '/api/discord/assignroles{x:/?}{method:.*}', self.apiDiscordAssignroles)
		self.Web.router.add_route('*', '/api/discord/twitchalerts{x:/?}{method:.*}', self.apiDiscordTwitchalerts)
		self.Web.router.add_route('*', '/api/discord/logs{x:/?}{method:.*}', self.apiDiscordLogs)