#api/db/

import json, requests, hashlib

def login(BASE, info={}, from_web=False, **kwargs):
	content = info.get("content", "")
	try:
		f = json.loads(content)
	except:
		f = {}

	password = f.get("password", "")
	login = f.get("login", "")

	if password == "" or login == "":
		class r (object):
			content = json.dumps(dict(error="missing_data")).encode("UTF-8")
			response = 400
			header = [('Content-Type', 'application/json')]
		return r

	#get user
	search_str = "data['loginname'] == '{0}' and data['password'] == '{1}'".format(login, hashlib.sha256(password.encode("UTF-8")).hexdigest())
	res=BASE.PhaazeDB.select(of="file_server/user", where=search_str)
	file_server_user = res['data'][0] if len(res['data']) > 0 else None

	if file_server_user == None:
		class r (object):
			content = json.dumps(dict(error="wrong_data")).encode("UTF-8")
			response = 401
			header = [('Content-Type', 'application/json')]
		return r

	new_session = BASE.moduls._Web_.Base.Utils.get_session_key()

	entry = dict(session_id = new_session, username=file_server_user['loginname'])
	BASE.PhaazeDB.insert(into="session/file_server", content=entry)

	class r (object):
		content = json.dumps(dict(fileserver_session=new_session)).encode("UTF-8")
		response = 200
		header = [('Content-Type', 'application/json')]
	return r
