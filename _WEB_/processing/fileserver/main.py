#BASE.moduls._Web_.Base.root.fileserver.main

import http.cookies as cookie
from importlib import reload
import json

def main(BASE, info, dirs):
	#/fileserver
	if len(info['path']) == 0:
		return fileserver(BASE, info)

	#leads to another site - /fileserver/[something]
	else:
		try:
			next_file = "dirs.fileserver.{0}.main.main".format(info['path'][0].lower())
			info['path'].pop(0)
			return eval(next_file+"(BASE, info, dirs)")

		except:
			return dirs.page_not_found.page_not_found(BASE, info, dirs)

def fileserver(BASE, info):
	if info["values"].get("login", False):
		return login_user(BASE, info)

	return_header = [('Content-Type','text/html')]

	if info['cookies'].get('fileserver_session', None) != None:
		return fileserver_main()
	else:
		return fileserver_login()

def fileserver_main():
	return_header = [('Content-Type','text/html')]
	site = open('_WEB_/content/fileserver/fileserver_main.html', 'r').read()
	nav = open('_WEB_/content/navbar_content.html', 'r').read()

	site = site.replace("<!-- Navbar -->", nav)

	class r (object):
		content = site.encode("UTF-8")
		response = 200
		header = return_header
	return r

def fileserver_login():
	return_header = [('Content-Type','text/html')]
	site = open('_WEB_/content/fileserver/fileserver_login.html', 'r').read()
	nav = open('_WEB_/content/navbar_content.html', 'r').read()

	site = site.replace("<!-- Navbar -->", nav)

	class r (object):
		content = site.encode("UTF-8")
		response = 200
		header = return_header
	return r

def login_user(BASE, info):
	content = info["content"]
	print(content)

	try:
		f = json.loads(content)
	except:
		f = {}

	print(f)
	password = f.get("login", "")
	login = f.get("password", "")

	if password == "" or login == "":
		class r (object):
			content = json.dumps(dict(error="missing_data")).encode("UTF-8")
			response = 200
			header = []
		return r

	new_session="NEED_TO_GET_DATA_FROM_DB"

	class r (object):
		content = json.dumps(dict(fileserver_session=new_session)).encode("UTF-8")
		response = 200
		header = []
	return r
