#Base.moduls._Web_.Base

import time, asyncio, re, json
import http.server

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
			return dict(path=path_parts, values=values)

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

		return dict(path=path_parts, values=values)

def process(BASE, info):
	print(info)

	class r(object):
		response = 200
		header = ("Content-Type", "application/json")
		content = str(vars(BASE)).encode("UTF-8")
	return r

class RequestHandler(http.server.BaseHTTPRequestHandler):

	def do_GET(self):

		information = Utils.parse_url(self.path)
		print(information)

		return_value = process(RequestHandler.BASE, information)

		self.send_response(return_value.response)
		self.send_header(return_value.header[0] ,return_value.header[1])
		self.end_headers()
		self.wfile.write(return_value.content)
		return

async def webserver(BASE):
	RequestHandler.BASE = BASE
	server = http.server.HTTPServer(('0.0.0.0', 8080), RequestHandler)
	server.serve_forever()

