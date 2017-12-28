import json, requests, discord

VERSION = "v6"
ROOT = "https://discordapp.com/api/{}/".format(VERSION)

def get_user(BASE, oauth_key=None, info={},from_web=False):
	"""Out only"""
	if from_web:
		class r (object):
			content = json.dumps(dict(error='forbidden', msg="system only")).encode("UTF-8")
			response = 403
			header = [('Content-Type', 'application/json')]
		return r

	if oauth_key == None: raise Exception

	try:
		t = requests.get(ROOT+"users/@me", headers={'Authorization': 'Bearer {}'.format(oauth_key)})
		return t.json()
	except Exception as e:
		raise e

def get_servers(BASE, info={}, from_web=False, **kwargs):
	"""In and Out"""
	content = info.get("content", "")
	try:
		f = json.loads(content)
	except:
		f = {}

	for key in kwargs:
		f[key] = kwargs[key]

	session_key = f.get("discord_session", None)
	if session_key == None:
		class r (object):
			content = json.dumps(dict(error='missing_session_key')).encode("UTF-8")
			response = 400
			header = [('Content-Type', 'application/json')]
		return r

	search_str = 'data["session"] == "{}"'.format(session_key)
	res = BASE.PhaazeDB.select(of="session/discord", where=search_str)

	#can't find session id DB
	if res['hits'] != 1:
		class r (object):
			return_header = [("Location", "/discord?error")]

			content = b""
			response = 302
			header = return_header
		return r

	obj = res['data'][0]

	#Cant get a access Key
	access_key = obj.get('access_token', None)
	if access_key == None:
		class r (object):
			return_header = [("Location", "/discord?error")]

			content = b""
			response = 302
			header = return_header
		return r

	try:
		servers = requests.get(ROOT+"users/@me/guilds", headers={'Authorization': 'Bearer {}'.format(access_key)})
		stuff = servers.json()
		for server in stuff:
			perm = discord.Permissions(permissions=server.get('permissions',0))
			if perm.manage_server or perm.administrator:
				server['manage'] = True
			else:
				server['manage'] = False
		class r (object):
			content = json.dumps(stuff)
			response = 200
			header = [('Content-Type', 'application/json')]
		return r

	except Exception as e:
		raise e

def login(BASE, info={}, from_web=False, **kwargs):
	"""In Only"""
	code = info.get("values",{}).get("code", None)

	if code == None:
		return_header = [("Location", "/discord?error")]
		class r (object):
			content = "".encode("UTF-8")
			response = 302
			header = return_header
		return r

	data = {'client_id': BASE.access.Discord_Phaaze_id,
			'client_secret': BASE.access.Discord_Phaaze_secret,
			'grant_type': 'authorization_code',
			'code': code,
			'redirect_uri': "http://phaaze.net/api/discord/login"}

	headers = {'Content-Type': 'application/x-www-form-urlencoded'}

	r = requests.post('https://discordapp.com/api/v6/oauth2/token', data, headers)
	r.raise_for_status()
	r=r.json()

	save_object = dict(
		session = BASE.moduls._Web_.Base.Utils.get_session_key(),
		access_token = r.get('access_token', None),
		token_type = r.get('token_type', None),
		refresh_token = r.get('refresh_token', None),
		scope = r.get('scope', None)
	)

	res = BASE.PhaazeDB.insert(into="session/discord", content=save_object)

	if res['status'] == "inserted":
		class r (object):
			return_header = [('Set-Cookie','discord_session='+save_object['session'] + "; Path=/"), ("Location", "/discord")]

			content = b""
			response = 302
			header = return_header
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

	session_key = f.get("discord_session", None)
	if session_key == None:
		class r (object):
			content = json.dumps(dict(error='missing_session_key')).encode("UTF-8")
			response = 400
			header = [('Content-Type', 'application/json')]
		return r

	res = BASE.PhaazeDB.delete(of="session/discord", where="data['session'] == '{}'".format(session_key))

	if res['hits'] == 1:
		class r (object):
			content = json.dumps(dict(msg='success')).encode("UTF-8")
			response = 200
			header = [('Content-Type', 'application/json')]
		return r
