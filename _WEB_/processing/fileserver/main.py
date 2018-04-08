#BASE.moduls._Web_.Base.root.fileserver.main

import http.cookies as cookie
from importlib import reload
import json, hashlib, random, string

def main(BASE, info, root):

	dump = dict()

	session = info.get('cookies', {}).get('fileserver_session', None)

	if session == None:
		return fileserver_login(BASE, info, dump)

	elif len(info['path']) == 0:
		return fileserver_main(BASE, info, dump)


	else:
		return root.page_not_found.page_not_found(BASE, info, root)

def fileserver_main(BASE, info, dump):
	return_header = [('Content-Type','text/html')]
	site = open('_WEB_/content/fileserver/fileserver_main.html', 'r').read()

	site = BASE.moduls._Web_.Utils.format_html_functions(BASE, site, infos = info)

	class r (object):
		content = site.encode("UTF-8")
		response = 200
		header = return_header
	return r

def fileserver_login(BASE, info, dump):
	return_header = [('Content-Type','text/html')]
	site = open('_WEB_/content/fileserver/fileserver_login.html', 'r').read()

	site = BASE.moduls._Web_.Utils.format_html_functions(BASE, site, infos = info)

	class r (object):
		content = site.encode("UTF-8")
		response = 200
		header = return_header
	return r
