#BASE-modules._Web_.Base

import re, sys
import ssl
from aiohttp import web

class root(object):

	def __init__(self, BASE):
		self.BASE = BASE
		self.response = self.send_Response
		self.format_html_regex = re.compile(r"\|>>>\((.+)\)<<<\|")
		self.html_root = open('_WEB_/content/root.html','r').read()
		self.html_header = BASE.modules._Web_.Utils.get_navbar

		self.web = self.init_web(self)
		self.api = self.init_api(self)

	def send_Response(self, **kwargs):
		already_set_header = kwargs.get('headers', dict())
		kwargs['headers'] = already_set_header
		kwargs['headers']['server'] =f"PhaazeOS v{self.BASE.version}"

		return web.Response(**kwargs)


	# Utility functions that are needed everywhere
	from _WEB_.Utils import format_html as format_html
	from _API_.Utils import get_user_informations as get_user_info
	from _API_.Utils import password as password
	from _API_.Utils import make_session_key as make_session_key

	# /api/ ...
	class init_api(object):
		def __init__(self, root):
			self.root = root

		from _API_.Base import nothing as nothing											#/api
		from _API_.Base import unknown as unknown											#/api/?
		from _API_.Base import action_not_allowed as action_not_allowed						#<400><401><402>
																							#
		from _API_.Account import login as account_login									#/api/account/login
		from _API_.Account import logout as account_logout									#/api/account/logout
		from _API_.Account import create as account_create									#/api/account/create
																							#
		from _API_.Admin import eval_command as admin_eval_command							#/api/account/create
																							#

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


def webserver(BASE):
	server = web.Application()
	root = BASE.modules._Web_.Base.root(BASE)
	BASE.web = server

	server.router.add_route('GET', '/.well-known/acme-challenge/{cert_file:.+}', root.web.cert)

	# /
	server.router.add_route('GET', '/', root.web.main)
	server.router.add_route('GET', '/favicon.ico', root.web.favicon)
	server.router.add_route('GET', '/login', root.web.login)
	server.router.add_route('GET', '/account', root.web.account)
	server.router.add_route('GET', '/account/create', root.web.account_create)
	server.router.add_route('GET', '/admin', root.web.admin_main)

	# /api
	server.router.add_route('GET', '/api{x:\/?}', root.api.nothing)
	server.router.add_route('*',   '/api/account/login', root.api.account_login)
	server.router.add_route('*',   '/api/account/logout', root.api.account_logout)
	server.router.add_route('*',   '/api/account/create', root.api.account_create)
	server.router.add_route('*',   '/api/admin/eval_command', root.api.admin_eval_command)
	server.router.add_route('GET', '/api/{path:.*}', root.api.unknown)

	# /js /img /css
	server.router.add_route('GET', '/img{file:.*}', root.web.img)
	server.router.add_route('GET', '/css{file:.*}', root.web.css)
	server.router.add_route('GET', '/js{file:.*}', root.web.js)

	# somewhere but i don't know
	server.router.add_route('*',   '/{x:.*}', root.web.page_not_found)

	###################################

	option_re = re.compile(r'^--(.+?)=(.*)$')
	all_args = dict()
	for arg in sys.argv[1:]:
		d = option_re.match(arg)
		if d != None:
			all_args[d.group(1)] = d.group(2)

	if all_args.get("http", "test") == "live":
		SSL = ssl.SSLContext()
		SSL.load_cert_chain('/etc/letsencrypt/live/phaaze.net/fullchain.pem', keyfile='/etc/letsencrypt/live/phaaze.net/privkey.pem')
		BASE.modules.Console.INFO("Started web server (p433/live)")
		web.run_app(server, handle_signals=False, ssl_context=SSL, port=443, print=False)
	else:
		BASE.modules.Console.INFO("Started web server (p900/test)")
		web.run_app(server, handle_signals=False, port=900, print=False)
