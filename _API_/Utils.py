#BASE.api.Utils

import json, requests, hashlib

# log in/out
# /api/login
def login(BASE, info={}, from_web=False, **kwargs):
	content = info.get("content", "")
	try:
		f = json.loads(content)
	except:
		f = {}

	password = f.get("password", "")
	phaaze_username = f.get("phaaze_username", "")

	if password == "" or phaaze_username == "":
		class r (object):
			content = json.dumps(dict(error="missing_data")).encode("UTF-8")
			response = 400
			header = [('Content-Type', 'application/json')]
		return r

	user = get_phaaze_user(BASE, phaaze_username=phaaze_username, password=password)

	if user == None:
		class r (object):
			content = json.dumps(dict(error="wrong_data")).encode("UTF-8")
			response = 401
			header = [('Content-Type', 'application/json')]
		return r

	new_session = BASE.moduls._Web_.Base.Utils.get_session_key()

	entry = dict(session = new_session, user_id=user['id'])
	BASE.PhaazeDB.insert(into="session/phaaze", content=entry)

	class r (object):
		content = json.dumps(dict(phaaze_session=new_session)).encode("UTF-8")
		response = 200
		header = [('Content-Type', 'application/json')]
	return r

# /api/logout
def logout(BASE, info={}, from_web=False, **kwargs):
	content = info.get("content", "")
	try:
		f = json.loads(content)
	except:
		f = {}

	session_key = info.get('cookies', {}).get("phaaze_session", None)
	if session_key == None:
		session_key = f.get('session', None)

	if session_key == None:
		class r (object):
			content = json.dumps(dict(error='missing_session_key')).encode("UTF-8")
			response = 400
			header = [('Content-Type', 'application/json')]
		return r

	res = BASE.PhaazeDB.delete(of="session/phaaze", where="data['session'] == '{}'".format(session_key))

	if res['hits'] == 1:
		class r (object):
			content = json.dumps(dict(msg='success')).encode("UTF-8")
			response = 200
			header = [('Content-Type', 'application/json')]
		return r

#get user infos

def get_phaaze_user(BASE, phaaze_username=None, password=None, session=None, api_token=None, **kwarg):

	#via username and password
	if phaaze_username != None and password != None:
		search_str = 'data["phaaze_username"] == "{}" '.format(phaaze_username)
		password = hashlib.sha256(password.encode("UTF-8")).hexdigest()
		search_str = search_str + "and data['password'] == '{}'".format(password)
		res = BASE.PhaazeDB.select(of="user", where=search_str)
		if len(res['data']) != 1:
			return None

		else:
			return res['data'][0]

	if session != None:
		search_str = 'data["session"] == "{}" '.format(session)
		res = BASE.PhaazeDB.select(of="session/phaaze", where=search_str)
		if len(res['data']) != 1:
			return None

		else:
			user_session = res['data'][0]

		search_str = 'int(data["id"]) == {} '.format(user_session.get('user_id',"0"))
		res = BASE.PhaazeDB.select(of="user", where=search_str)
		if len(res['data']) != 1:
			return None

		else:
			return res['data'][0]

#discord

def get_discord_user_by_session(BASE, session):

	search_str = 'data["session"] == "{}"'.format(session)
	res = BASE.PhaazeDB.select(of="session/discord", where=search_str)
	if len(res['data']) == 0:
		return None

	return res['data'][0]
