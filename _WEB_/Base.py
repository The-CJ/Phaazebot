#BASE.modules._Web_.Base

import re
import ssl
import asyncio, json
from aiohttp import web
from Utils import CLI_Args

class root(object):

	def __init__(self, BASE):
		self.BASE = BASE
		self.response = self.send_Response
		self.format_html_regex = re.compile(r"\|>>>\((.+?)\)<<<\|")
		self.html_root = open('_WEB_/content/root.html','r').read()
		self.html_header = BASE.modules._Web_.Utils.get_navbar

		self.web = self.init_web(self)
		self.api = self.init_api(self)

	def send_Response(self, **kwargs):
		already_set_header = kwargs.get('headers', dict())
		kwargs['headers'] = already_set_header
		kwargs['headers']['server'] =f"PhaazeOS v{self.BASE.version}"

		return web.Response(**kwargs)

	@web.middleware
	async def middleware_handler(self, request, handler):
		try:
			response = await handler(request)
			return response
		except web.HTTPException as HTTPEx:
			return self.response(
				body=json.dumps(dict(msg=HTTPEx.reason, status=HTTPEx.status)),
				status=HTTPEx.status,
				content_type='application/json'
			)
		except Exception as e:
			self.BASE.modules.Console.ERROR(str(e))

	# Utility functions that are needed everywhere
	from _WEB_.Utils import format_html as format_html
	from _API_.Utils import check_role as check_role
	from _API_.Utils import get_user_informations as get_user_info
	from _API_.Utils import password as password
	from _API_.Utils import make_session_key as make_session_key

	# /api/ ...
	class init_api(object):
		def __init__(self, root):
			self.root = root

		from _API_.Base import nothing as nothing											#/api
		from _API_.Base import unknown as unknown											#/api/? <400>
		from _API_.Base import action_not_allowed as action_not_allowed						#<401><402>
																							#
		from _API_.Account import main as account											#/api/account
																							#
		from _API_.Admin import eval_command as admin_eval_command							#/api/admin/eval_command
		from _API_.Admin import status as admin_status										#/api/admin/status
		from _API_.Admin import control as admin_control									#/api/admin/control
		from _API_._Admin_.manage_user import main as admin_manage_user						#/api/admin/manage-user
		from _API_._Admin_.manage_type import main as admin_manage_type						#/api/admin/manage-type
		from _API_._Admin_.manage_image import main as admin_manage_image					#/api/admin/manage-image
																							#
		from _API_.Wiki import main as wiki													#/api/wiki

	# / ...
	class init_web(object):																	#
		def __init__(self, root):															#
			self.root = root																#
																							#
		from _WEB_.js.Base import main as js												#/js
		from _WEB_.css.Base import main as css												#/css
		from _WEB_.img.Base import main as img												#/img
																							#
		from _WEB_.processing.Base import get_favicon as favicon							#/favicon.ico
		from _WEB_.processing.Base import main as main										#/
		from _WEB_.processing.Base import cert as cert										#/.well-known/acme-challenge/
		from _WEB_.processing.page_not_found import main as page_not_found					#<404>
		from _WEB_.processing.action_not_allowed import main as action_not_allowed			#<400/401/402>
																							#
		from _WEB_.processing.account.main import login as login							#/login
		from _WEB_.processing.account.main import account as account						#/account
		from _WEB_.processing.account.create import create as account_create				#/account/create
																							#
		from _WEB_.processing.admin.admin import main as admin_main							#/admin
		from _WEB_.processing.admin.manage_user import main as admin_manage_user			#/admin/manage-user
		from _WEB_.processing.admin.manage_type import main as admin_manage_type			#/admin/manage-type
		from _WEB_.processing.admin.manage_system import main as admin_manage_system		#/admin/manage-system
		from _WEB_.processing.admin.manage_image import main as admin_manage_image			#/admin/manage-image
																							#
		from _WEB_.processing.discord.invite import main as discord_invite					#/discord/invite
																							#
		from _WEB_.processing.wiki.wiki import main as wiki									#/wiki

def webserver(BASE):
	server = web.Application(client_max_size=BASE.limit.WEB_CLIENT_MAX_SIZE)
	root = BASE.modules._Web_.Base.root(BASE)
	BASE.web = server

	server.router.add_route('GET', '/.well-known/acme-challenge/{cert_file:.+}', root.web.cert)

	# /
	server.router.add_route('GET', '/', root.web.main)
	server.router.add_route('GET', '/favicon.ico', root.web.favicon)
	server.router.add_route('GET', '/login', root.web.login)
	server.router.add_route('GET', '/account', root.web.account)
	server.router.add_route('GET', '/account/create', root.web.account_create)
	server.router.add_route('GET', '/wiki{x:/?}{site:.*}', root.web.wiki)

	# /admin
	server.router.add_route('GET', '/admin', root.web.admin_main)
	server.router.add_route('GET', '/admin/manage-user', root.web.admin_manage_user)
	server.router.add_route('GET', '/admin/manage-type', root.web.admin_manage_type)
	server.router.add_route('GET', '/admin/manage-system', root.web.admin_manage_system)
	server.router.add_route('GET', '/admin/manage-image', root.web.admin_manage_image)

	# /discord
	server.router.add_route('GET', '/discord/invite', root.web.discord_invite)

	# /api
	server.router.add_route('GET', '/api{x:\/?}', root.api.nothing)
	server.router.add_route('*',   '/api/account{x:/?}{method:.*}', root.api.account)
	server.router.add_route('*',   '/api/admin/eval_command', root.api.admin_eval_command)
	server.router.add_route('*',   '/api/admin/status', root.api.admin_status)
	server.router.add_route('*',   '/api/admin/control', root.api.admin_control)
	server.router.add_route('*',   '/api/admin/manage-user{x:/?}{method:.*}', root.api.admin_manage_user)
	server.router.add_route('*',   '/api/admin/manage-type{x:/?}{method:.*}', root.api.admin_manage_type)
	server.router.add_route('*',   '/api/admin/manage-image{x:/?}{method:.*}', root.api.admin_manage_image)
	server.router.add_route('*',   '/api/wiki{x:/?}{method:.*}', root.api.wiki)
	server.router.add_route('*',   '/api/{path:.*}', root.api.unknown)

	# /js /img /css
	server.router.add_route('GET', '/img{file:.*}', root.web.img)
	server.router.add_route('GET', '/css{file:.*}', root.web.css)
	server.router.add_route('GET', '/js{file:.*}', root.web.js)

	# somewhere but i don't know
	server.router.add_route('*',   '/{x:.*}', root.web.page_not_found)

	# main handler to catch errors
	#server.middlewares.append(root.middleware_handler)

	###################################

	port = 900
	ssl_context = None

	if CLI_Args.get("http", "test") == "live":
		port = 443
		ssl_context = ssl.SSLContext()
		ssl_context.load_cert_chain('/etc/letsencrypt/live/phaaze.net/fullchain.pem', keyfile='/etc/letsencrypt/live/phaaze.net/privkey.pem')
		BASE.modules.Console.INFO("Started web server (p433/live)")
	elif CLI_Args.get("http", "test") == "unsecure":
		port = 80
		BASE.modules.Console.INFO("Started web server (p80/http-unsecure)")
	elif CLI_Args.get("http", "test") == "error_ssl":
		port = 443
		BASE.modules.Console.INFO("Started web server (p433/https-no_ssl)")
	else:
		BASE.modules.Console.INFO("Started web server (p900/test)")

	web.run_app(server, handle_signals=False, port=port, ssl_context=ssl_context, print=False)
