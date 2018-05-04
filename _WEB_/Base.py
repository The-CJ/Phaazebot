#BASE.modules._Web_.Base

import time, datetime, asyncio, re, json
import http.server
import urllib.parse as url_parse
import hashlib, random, string, ssl

the_list_of_endpoint_that_gets_always_triggered_by_annoying_bots_on_search_of_something__That_i_will_anwnser_with_a_toaster = [
	'/phpMyAdmin', '/php', '/pma', '/ccvv', '/index.php', '/robots.txt', '/cfide', '/webman',
	'/hnap1', '/webman', '/vendor', '/http:', '/zabbit', '/myadmin', '/wp-admin'
]

class root(object):

	class discord(object):
		import _WEB_.processing.discord.main as main							#/discord
		import _WEB_.processing.discord.dashboard as dashboard					#/discord/dashboard
		import _WEB_.processing.discord.invite as invite						#/discord/invite
		import _WEB_.processing.discord.custom as custom						#/discord/custom
																				#
	class fileserver(object):													#
		import _WEB_.processing.fileserver.main as main							#/fileserver
																				#
	class wiki(object):															#
		import _WEB_.processing.wiki.main as main								#/wiki
																				#
	class admin(object):														#
		import _WEB_.processing.admin.admin as admin							#/admin
																				#
	class account(object):														#
		import _WEB_.processing.account.main as account							#/account
																				#
	import _WEB_.js.main as js													#/js
	import _WEB_.css.main as css												#/css
	import _WEB_.img.main as img												#/img
																				#
	import _WEB_.processing.main as main										#/
	import _WEB_.processing.page_not_found as page_not_found					#<404>
	import _WEB_.processing.action_not_allowed as action_not_allowed			#<400/401/402>


class Utils(object):

	def parse_url(url):
		url = url_parse.unquote_plus(url)
		raw_list = url.split('?')

		#get path parts
		path_parts = raw_list[0].split("/")
		while '' in path_parts:
			path_parts.remove('')

		#No more vars? -> return
		if len(raw_list) == 1:
			values = dict()
			return dict(raw_path= url, path=path_parts, values=values)

		#more vars
		other_arguments = raw_list[1]
		all_args = other_arguments.split("&")
		if len(all_args) == 0:
			all_args = other_arguments
		values = dict()
		for arg in all_args:
			hit = re.search(r"(\w+)(=(\S+)|=)?", arg)
			if hit == None: continue

			if hit.group(2) == None and hit.group(3) == None:
				values[hit.group(1)] = True
			else:
				values[hit.group(1)] = hit.group(3)

		return dict(raw_path= url, path=path_parts, values=values)

	def parse_cookies(head):
		kekse = head.get('Cookie', None)
		if kekse == None: return {}

		cookiejar = {}
		for keks in kekse.split(";"):
			try:
				key, value = keks.split("=")
				cookiejar[key.replace(" ", "")] = value.replace(" ", "")
			except:
				pass
		return cookiejar

	def get_content(rfile, headers):
		try: length = int(headers["Content-Length"])
		except: length = 0

		content = rfile.read(length)
		return content

	def get_session_key():
		stime = hashlib.sha1( str(datetime.datetime.now()).encode("UTF-8") ).hexdigest()
		snonce = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(8))

		key = str(stime) + str(snonce)
		return key

def process(BASE, info):

	if ""=="":
		r = root.main.main(BASE, info, root)

	return r

class RequestHandler(http.server.BaseHTTPRequestHandler):

	def do_POST(self):
		self.do_GET()

	def do_GET(self):

		if not RequestHandler.BASE.active.web: return

		if self.path.lower() in the_list_of_endpoint_that_gets_always_triggered_by_annoying_bots_on_search_of_something__That_i_will_anwnser_with_a_toaster:
			return

		#path, raw_path, values
		information = Utils.parse_url(self.path)
		information['header'] = self.headers
		information['cookies'] = Utils.parse_cookies(self.headers)
		information['content'] = Utils.get_content(self.rfile, self.headers)

		return_value = process(RequestHandler.BASE, information)
		if return_value == None:
			class r(object):
				response=500
				header=[('Content-Type','text/html')]
				content=b""

			return_value = r

		#200, 404, etc
		self.send_response(return_value.response)

		#send all head vars
		for head_value in return_value.header:
			self.send_header(head_value[0] ,head_value[1])

		#end headers
		self.end_headers()

		#send content
		if type(return_value.content) is not bytes: return_value.content = str(return_value.content).encode("UTF-8")
		self.wfile.write(return_value.content)
		self.wfile.flush()

	def log_message(self, format, *args):
		return

async def webserver(BASE):
	RequestHandler.BASE = BASE
	server = http.server.HTTPServer(('0.0.0.0', 80), RequestHandler)
	# server = ssl.wrap_socket(server.socket, certfile=None, server_side=True)
	server.serve_forever()

