#BASE.moduls._Web_.Base.root.fileserver.main

import http.cookies as cookie
from importlib import reload
import json, hashlib, random, string

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
	try:
		f = json.loads(content)
	except:
		f = {}

	password = f.get("password", "")
	login = f.get("login", "")

	if password == "" or login == "":
		class r (object):
			content = json.dumps(dict(error="missing_data")).encode("UTF-8")
			response = 200
			header = []
		return r

	#get user
	search_str = "data['loginname'] == '{0}' and data['password'] == '{1}'".format(login, hashlib.sha256(password.encode("UTF-8")).hexdigest())
	res=BASE.PhaazeDB.select(of="file_server/user", where=search_str)
	file_server_user = res['data'][0] if len(res['data']) > 0 else None

	if file_server_user == None:
		class r (object):
			content = json.dumps(dict(error="wrong_data")).encode("UTF-8")
			response = 200
			header = []
		return r

	new_session = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(16))

	entry = dict(session_id = new_session, username=file_server_user['loginname'])
	BASE.PhaazeDB.insert(into="session/file_server", content=entry)

	class r (object):
		content = json.dumps(dict(fileserver_session=new_session)).encode("UTF-8")
		response = 200
		header = []
	return r
