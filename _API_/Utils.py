import json, requests, hashlib

#admin

def authorise_admin(BASE, session=None, auth_key=None, username=None, password=None):
	if session != None:
		admin = get_admin_by_session(BASE, session)
		if admin != None: return admin

	if auth_key != None:
		pass
		#TODO: admin api keys

	if username != None and password != None:
		search_str = "data['username'] == '{0}' and data['password'] == '{1}'".format(username, hashlib.sha256(password.encode("UTF-8")).hexdigest())
		res=BASE.PhaazeDB.select(of="admin/user", where=search_str)
		admin = res['data'][0] if len(res['data']) > 0 else None
		if admin != None: return admin

	return None

def get_admin_by_session(BASE, session):
	r_value = None

	admin_session =  BASE.PhaazeDB.select(of="session/admin", where='data["session"] == "{}"'.format(session))

	if admin_session['hits'] == 1:
		admin_user_id = admin_session['data'][0].get("user_id", "")
		admin_user = BASE.PhaazeDB.select(of="admin/user", where='data["id"] == {}'.format(admin_user_id))

		if admin_user['hits'] == 1:
			r_value = admin_user['data'][0]

	return r_value

def get_admin_by_url_values(BASE, info):
	r_value = None

	username = info.get("user", "")
	password = hashlib.sha256(info.get("password", "").encode("UTF-8")).hexdigest()

	admin_user = BASE.PhaazeDB.select(of="admin/user", where='data["username"] == "{0}" and data["password"] == "{1}"'.format(username, password))
	if admin_user['hits'] == 1:
		r_value = admin_user['data'][0]

	return r_value

#discord

def get_discord_user_by_session(BASE, session):

	search_str = 'data["session"] == "{}"'.format(session)
	res = BASE.PhaazeDB.select(of="session/discord", where=search_str)
	if len(res['data']) == 0:
		return None

	return res['data'][0]
