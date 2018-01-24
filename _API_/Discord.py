#api/discord/

import json, requests, discord, asyncio, hashlib

VERSION = "v6"
ROOT = "https://discordapp.com/api/{}/".format(VERSION)

def change_bot_name(BASE, info={}, from_web=False, **kwargs):
	"""require admin"""
	#local call
	if not from_web:
		#get name
		bot_name = info.get("bot_name",None)
		if bot_name == None:
			bot_name = kwargs.get("bot_name", None)

		if bot_name == None:
			raise AttributeError("missing 'bot_name' field")

		func = BASE.phaaze.edit_profile(username=str(bot_name))
		f = asyncio.ensure_future(func, loop=BASE.Discord_loop)
	else:
		pass

def change_bot_picture(BASE, info={}, from_web=False, **kwargs):
	"""require admin"""
	#local call
	if not from_web:
		#get pic
		picture = kwargs.get("picture", None)

		if picture == None:
			raise AttributeError("missing 'picture' field")

		if type(picture) is not bytes:
			raise AttributeError("field 'picture' must be bytes")

		func = BASE.phaaze.edit_profile(avatar=picture)
		f = asyncio.ensure_future(func, loop=BASE.Discord_loop)

	if from_web:
		valid = False

		#via session cookie
		session = info.get("cookies",{}).get("admin_session", None)
		if session != None:
			#there give me a session -> check it
			admin = BASE.api.utils.get_admin_by_session(BASE, session)

			if admin == None:
				class r (object):
					content = json.dumps(dict(error="unauthorized", msg="session or user not found")).encode("UTF-8")
					response = 400
					header = [('Content-Type', 'application/json')]
				return r

			if admin.get("type", None) == "superadmin" or admin.get("type", None) == "admin":
				func = BASE.phaaze.edit_profile(avatar=info['content'])
				f = asyncio.ensure_future(func, loop=BASE.Discord_loop)
				class r (object):
					content = json.dumps(dict(msg="ok")).encode("UTF-8")
					response = 200
					header = [('Content-Type', 'application/json')]
				return r

			else:
				class r (object):
					content = json.dumps(dict(error='unauthorized', msg="user must have 'admin' or higher")).encode("UTF-8")
					response = 401
					header = [('Content-Type', 'application/json')]
				return r

		#via url calls wiht values
		cred = info.get("values",{})
		if cred.get("user", None) != None and cred.get("password", None) != None:
			admin = BASE.api.utils.get_admin_by_url_values(BASE, info.get("values",{}))

			if admin == None:
				class r (object):
					content = json.dumps(dict(error="unauthorized", msg="'user' or 'password' wrong")).encode("UTF-8")
					response = 401
					header = [('Content-Type', 'application/json')]
				return r

			if admin.get("type", None) == "superadmin" or admin.get("type", None) == "admin":
				func = BASE.phaaze.edit_profile(avatar=info['content'])
				f = asyncio.ensure_future(func, loop=BASE.Discord_loop)
				class r (object):
					content = json.dumps(dict(msg="ok")).encode("UTF-8")
					response = 200
					header = [('Content-Type', 'application/json')]
				return r
			else:
				class r (object):
					content = json.dumps(dict(error='unauthorized', msg="user must have 'admin' or higher")).encode("UTF-8")
					response = 401
					header = [('Content-Type', 'application/json')]
				return r

		class r (object):
			content = json.dumps(dict(error="unauthorized",msg="missing auth.")).encode("UTF-8")
			response = 401
			header = [('Content-Type', 'application/json')]
		return r

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

def get_server(BASE, info={}, from_web=False, **kwargs):
	"""Out only"""
	if from_web:
		class r (object):
			content = json.dumps(dict(error='forbidden', msg="system only")).encode("UTF-8")
			response = 403
			header = [('Content-Type', 'application/json')]
		return r

	server_id = kwargs.get("server_id", None)

	if server_id == None: raise Exception

	try:
		t = requests.get(ROOT+"guilds/{}".format(server_id), headers={'Authorization': 'Bot {}'.format(BASE.access.Discord_Phaaze)})
		return t.json()
	except Exception as e:
		raise e

def get_servers(BASE, info={}, from_web=False, **kwargs):
	"""In and Out"""


	session_key = info.get('cookies', {}).get("discord_session", None)
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

	auth_discord_user= BASE.api.discord.get_user(BASE, oauth_key=r.get('access_token', None))

	save_object = dict(
		session = BASE.moduls._Web_.Base.Utils.get_session_key(),
		access_token = r.get('access_token', None),
		token_type = r.get('token_type', None),
		refresh_token = r.get('refresh_token', None),
		scope = r.get('scope', None),
		user_info = auth_discord_user
	)

	res = BASE.PhaazeDB.insert(into="session/discord", content=save_object)

	if res['status'] == "inserted":
		class r (object):
			return_header = [('Set-Cookie','discord_session='+save_object['session'] + "; Path=/;"), ("Location", "/discord")]

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

def get_server_custom_commands(BASE, info={}, from_web=False, **kwargs):
	"""Out Only"""

	server_id = kwargs.get('id', None)
	if server_id == None:
		server_id = info.get('values', {}).get('id', None)
	if server_id == None:
		try:
			con = json.loads(info.get('content', ""))
			server_id = con.get('id', None)
		except Exception as e:
			pass

	if server_id == None:
		if from_web:
			class r (object):
				content = json.dumps(dict(status='error', msg="missing 'id' field")).encode("UTF-8")
				response = 400
				header = [('Content-Type', 'application/json')]
			return r
		else:
			raise AttributeError("missing 'id' value")


	x = BASE.moduls.Utils.get_server_file(BASE, server_id, prevent_new=True)
	save_settings = BASE.call_from_async(x ,BASE.Discord_loop)

	if save_settings == None: save_settings = {}

	all_commands = save_settings.get('commands', [])

	if from_web:
		class r (object):
			content = json.dumps(dict(status='success', data=all_commands)).encode("UTF-8")
			response = 200
			header = [('Content-Type', 'application/json')]
		return r
	else:
		raise all_commands

def delete_custom_command(BASE, info={}, from_web=False, **kwargs):

	#get vars
	server_id = kwargs.get('server_id', None)
	trigger = kwargs.get('trigger', None)

	if server_id == None or trigger == None:
		server_id = info.get('values', {}).get('server_id', None)
		server_id = info.get('values', {}).get('trigger', None)

	if server_id == None or trigger == None:
		try:
			con = json.loads(info.get('content', ""))
			server_id = con.get('server_id', None)
			trigger = con.get('trigger', None)
		except Exception as e:
			print('invalid json')
			pass

	if server_id == None or trigger == None:
		if from_web:
			class r (object):
				content = json.dumps(dict(status='error', msg="missing 'server_id' or 'trigger' field")).encode("UTF-8")
				response = 400
				header = [('Content-Type', 'application/json')]
			return r
		else:
			raise AttributeError("missing 'server_id' or 'trigger' value")

	#auth
	auth = False
	if not from_web: #intern call
		auth = True

	if not auth: #call from outside, need auth

		session = info['cookies'].get('discord_session', None)
		discord_user = BASE.api.utils.get_discord_user_by_session(BASE, session)

		try:
			discord_server = BASE.phaaze.get_server(server_id)
			discord_member = discord_server.get_member(discord_user.get('user_info', {}).get('id', None) )
			perm = discord_member.server_permissions
			if perm.manage_server or perm.administrator:
				auth = True
		except:
			pass

	if not auth: # not authorized
		class r (object):
			content = json.dumps(dict(status='error', msg="unauthorized")).encode("UTF-8")
			response = 402
			header = [('Content-Type', 'application/json')]
		return r

	#get server file
	x = BASE.moduls.Utils.get_server_file(BASE, server_id, prevent_new=True)
	save_settings = BASE.call_from_async(x ,BASE.Discord_loop)

	#get command -> delete
	found = False
	for cmd in save_settings.get('commands',[]):
		if cmd['trigger'] == trigger:
			save_settings['commands'].remove(cmd)
			found = True

	#non found
	if not found:
		if from_web:
			class r (object):
				content = json.dumps(dict(status='error', msg="no command with trigger: '{}'".format(trigger))).encode("UTF-8")
				response = 400
				header = [('Content-Type', 'application/json')]
			return r
		else:
			raise AttributeError("no command found with: "+trigger)

	#finish
	with open("SERVERFILES/{0}.json".format(server_id), "w") as save:
		json.dump(save_settings, save)
		setattr(BASE.serverfiles, "server_"+server_id, save_settings)

		if from_web:
			class r (object):
				content = json.dumps(dict(status='success', msg="command: '{}' deleted".format(trigger))).encode("UTF-8")
				response = 200
				header = [('Content-Type', 'application/json')]
			return r
		else:
			return True










