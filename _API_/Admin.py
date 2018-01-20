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

	admin_user = BASE.api.utils.authorise_admin(BASE, username=login, password=password)

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
	admin = BASE.api.utils.authorise_admin(BASE, session=session)
	if admin.get('type', None) == 'superadmin':
		module = info['values'].get('modul',None)
		if module == None: return

		if eval("BASE.active.{} == True".format(module)):
			setattr(BASE.active, module, False)

		else:
			setattr(BASE.active, module, True)

def edit_file_content(BASE, info={}, from_web=False, **kwargs):
	if not from_web: return

	#start auth
	session = info.get("cookies",{}).get("admin_session", None)
	auth_key = info.get("values",{}).get("auth_key", None)
	username = info.get("values",{}).get("username", None)
	passwd = info.get("values",{}).get("passwords", None)

	admin = BASE.api.utils.authorise_admin(BASE, session=session, auth_key=auth_key, username=username, password=passwd)
	if admin == None: admin = {}

	#end auth

	if admin.get('type', None) != 'superadmin':
		class r (object):
			content = json.dumps(dict(status='error', msg='unauthorised')).encode("UTF-8")
			response = 400
			header = [('Content-Type', 'application/json')]
		return r

	content = info['content']
	file = info['values'].get('file', None)
	if file == None:
		class r (object):
			content = json.dumps(dict(status='error', msg='no_file_path')).encode("UTF-8")
			response = 400
			header = [('Content-Type', 'application/json')]
		return r

	overwrite = open(file ,'wb')
	overwrite.write(content)
	overwrite.close()

	class r (object):
		content = json.dumps(dict(status='success', msg='edited')).encode("UTF-8")
		response = 200
		header = [('Content-Type', 'application/json')]
	return r
