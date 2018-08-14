#BASE.modules._Web_.Base

import re
import ssl
from aiohttp import web

class root(object):

	def __init__(self, BASE):
		self.BASE = BASE
		self.response = web.Response
		self.format_html_regex = re.compile(r"\|>>>(.+)<<<\|")

		self.web = self.init_web(self)
		self.api = self.init_api(self)

	# Utility functions that are needed everywhere
	from _WEB_.Utils import format_html_functions as format_html
	from _API_.Utils import get_user_informations as get_user_info
	from _API_.Utils import password as password
	from _API_.Utils import make_session_key as make_session_key

	# /api/ ...
	class init_api(object):
		def __init__(self, root):
			self.root = root

		from _API_.Base import nothing as nothing											#/api
		from _API_.Base import unknown as unknown											#/api/?
																							#
		from _API_.Utils import login as login												#/api/login
		from _API_.Utils import logout as logout											#/api/logout
																							#
		#only temoraly?																		#
		from _API_.Base import games_webosu as games_webosu									#/api/games/webosu

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

	# class discord(object):																#
	# 	import _WEB_.processing.discord.main as main										#/discord
	# 	import _WEB_.processing.discord.dashboard as dashboard								#/discord/dashboard
	# 	import _WEB_.processing.discord.invite as invite									#/discord/invite
	# 	import _WEB_.processing.discord.custom as custom									#/discord/custom
	# 																						#
	# class fileserver(object):																#
	# 	import _WEB_.processing.fileserver.main as main										#/fileserver
	# 																						#
	# class wiki(object):																	#
	# 	import _WEB_.processing.wiki.main as main											#/wiki
	# 																						#
	# class admin(object):																	#
	# 	import _WEB_.processing.admin.admin as admin										#/admin
	# 																						#
	# class account(object):																#
	# 	import _WEB_.processing.account.main as account										#/account

def webserver(BASE):
	server = web.Application()
	root = BASE.modules._Web_.Base.root(BASE)
	BASE.web = server

	server.router.add_route('GET', '/.well-known/acme-challenge/{cert_file:.+}', root.web.cert)

	# main
	server.router.add_route('GET', '/', root.web.main)
	server.router.add_route('GET', '/favicon.ico', root.web.favicon)

	# /api
	server.router.add_route('GET', '/api{x:\/?}', root.api.nothing)
	server.router.add_route('*',   '/api/games/webosu', root.api.games_webosu)
	server.router.add_route('*',   '/api/login', root.api.login)
	server.router.add_route('*',   '/api/logout', root.api.logout)
	server.router.add_route('GET', '/api/{path:.*}', root.api.unknown)

	# /js /img /css
	server.router.add_route('GET', '/img{file:.*}', root.web.img)
	server.router.add_route('GET', '/css{file:.*}', root.web.css)
	server.router.add_route('GET', '/js{file:.*}', root.web.js)

	# somewhere but i don't know
	server.router.add_route('*',   '/{x:.*}', root.web.page_not_found)

	###################################

	SSL = ssl.SSLContext()
	SSL.load_cert_chain('/etc/letsencrypt/live/phaaze.net/fullchain.pem', keyfile='/etc/letsencrypt/live/phaaze.net/privkey.pem')
	web.run_app(server, handle_signals=False, ssl_context=SSL, port=443, print=False)
