#api/admin/

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
	search_str = "data['username'] == '{0}' and data['password'] == '{1}'".format(login, hashlib.sha256(password.encode("UTF-8")).hexdigest())
	res=BASE.PhaazeDB.select(of="admin/user", where=search_str)
	res_=BASE.PhaazeDB.select(of="admin/user")
	admin_user = res['data'][0] if len(res['data']) > 0 else None

	if admin_user == None:
		class r (object):
			content = json.dumps(dict(error="wrong_data")).encode("UTF-8")
			response = 401
			header = [('Content-Type', 'application/json')]
		return r

	new_session = BASE.moduls._Web_.Base.Utils.get_session_key()

	entry = dict(session = new_session, user_id=admin_user['id'])
	BASE.PhaazeDB.insert(into="session/admin", content=entry)

	class r (object):
		content = json.dumps(dict(admin_user=new_session)).encode("UTF-8")
		response = 200
		header = [('Content-Type', 'application/json')]
	return r

def logout(BASE, info={}, from_web=False, **kwargs):
	"""In Only"""
	content = info.get("content", "")
	try:
		f = json.loads(content)
	except:
		f = {}

	for key in kwargs:
		f[key] = kwargs[key]

	session_key = f.get("admin_session", None)
	if session_key == None:
		class r (object):
			content = json.dumps(dict(error='missing_session_key')).encode("UTF-8")
			response = 400
			header = [('Content-Type', 'application/json')]
		return r

	res = BASE.PhaazeDB.delete(of="session/admin", where="data['session'] == '{}'".format(session_key))

	if res['hits'] == 1:
		class r (object):
			content = json.dumps(dict(msg='success')).encode("UTF-8")
			response = 200
			header = [('Content-Type', 'application/json')]
		return r

def toggle_moduls(BASE, info={}, from_web=False, **kwargs):
	"""toggle main Moduls status"""
	session = info.get("cookies",{}).get("admin_session", None)
	admin = BASE.api.utils.get_admin_by_session(BASE, session)
	if admin.get('type', None) == 'superadmin':
		module = info['values'].get('modul',None)
		if module == None: return

		if eval("BASE.active.{} == True".format(module)):
			setattr(BASE.active, module, False)

		else:
			setattr(BASE.active, module, True)
