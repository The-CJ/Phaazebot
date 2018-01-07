import json, requests, hashlib

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
