#BASE.moduls._Web_.Base.root.fileserver.main

import http.cookies as cookie
from importlib import reload
import json, hashlib, random, string

def main(BASE, info, root):
	#/fileserver
	if len(info['path']) == 0:
		return fileserver(BASE, info)

	#leads to another site - /fileserver/[something]
	else:
		try:
			next_file = "root.fileserver.{0}.main.main".format(info['path'][0].lower())
			info['path'].pop(0)
			return eval(next_file+"(BASE, info, root)")

		except:
			return root.page_not_found.page_not_found(BASE, info, root)

def fileserver(BASE, info):
	if info["values"].get("login", False):
		return login_user(BASE, info)

	return_header = [('Content-Type','text/html')]

	if info['cookies'].get('fileserver_session', None) != None:

		return fileserver_main(BASE)
	else:
		return fileserver_login(BASE)

def fileserver_main(BASE):
	return_header = [('Content-Type','text/html')]
	site = open('_WEB_/content/fileserver/fileserver_main.html', 'r').read()

	site = site.replace("<!-- Navbar -->", BASE.moduls._Web_.Utils.get_navbar(active='db'))

	class r (object):
		content = site.encode("UTF-8")
		response = 200
		header = return_header
	return r

def fileserver_login(BASE):
	return_header = [('Content-Type','text/html')]
	site = open('_WEB_/content/fileserver/fileserver_login.html', 'r').read()

	site = site.replace("<!-- Navbar -->", BASE.moduls._Web_.Utils.get_navbar(active='db'))

	class r (object):
		content = site.encode("UTF-8")
		response = 200
		header = return_header
	return r
