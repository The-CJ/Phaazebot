#BASE.moduls._Web_.Base

import time, asyncio, re, json
import http.server

class root(object):

	import _WEB_.js.main as js

	import _WEB_.processing.main as main
	import _WEB_.processing.page_not_found as page_not_found

class Utils(object):

	def parse_url(url):
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

def process(BASE, info):

	print(info)

	if ""=="":#try:
		r = root.main.main(BASE, info, root)

	#except:
	#	class r(object):
	#		content = json.dumps(dict(error="no one knows what, but something was wrong")).encode(encoding='utf_8')
	#		response = 500
	#		header = [('Content-Type','application/json')]

	return r

class RequestHandler(http.server.BaseHTTPRequestHandler):

	def do_GET(self):

		information = Utils.parse_url(self.path)
		print(information)

		return_value = process(RequestHandler.BASE, information)

		#200, 404, etc
		self.send_response(return_value.response)

		#send all head vars
		for head_value in return_value.header:
			self.send_header(head_value[0] ,head_value[1])

		#end headers
		self.end_headers()

		#send content
		self.wfile.write(return_value.content)
		return

	def log_message(self, format, *args):
		return

async def webserver(BASE):
	RequestHandler.BASE = BASE
	server = http.server.HTTPServer(('0.0.0.0', 8080), RequestHandler)
	server.serve_forever()

