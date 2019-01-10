
import asyncio, json
import hashlib, random, string

#get user infos
async def get_user_informations(self, request, **kwargs):

	_GET = dict()
	_POST = dict()
	_JSON = dict()

	try:
		_GET = request.query
	except:
		pass

	try:
		_POST = await request.post()
	except:
		pass

	try:
		_JSON = await request.json()
	except:
		pass

	# All vars have the same Auth way: Systemcall var -> POST -> JSON Content -> GET

	#via session from header
	phaaze_session = request.headers.get('phaaze_session', None)
	#or cookie
	if phaaze_session == None:
		phaaze_session = request.cookies.get('phaaze_session', None)
	if phaaze_session != None:
		join_user_roles = dict(of="role", store="role", where="role['id'] in user['role']", fields=["name"])
		join_user = dict(of="user", store="user", where="session['user_id'] == user['id']", join=join_user_roles)
		res = self.BASE.PhaazeDB.select(of="session/phaaze", where=f'session["session"] == {json.dumps(phaaze_session)}', store="session", join=join_user)

		sess = res.get('data', [])
		if len(sess) == 1:
			s = sess[0]
			all_user = s.get('user', [])
			if len(all_user) == 1:
				user = all_user[0]
				user['role'] = [r['name'] for r in user.get('role', []) if r.get('name', False)]
				return user

	#via api token
	phaaze_token = kwargs.get('phaaze_token', None)
	if phaaze_token == None:
		phaaze_token = _POST.get('phaaze_token', None)
	if phaaze_token == None:
		phaaze_token = _JSON.get('phaaze_token', None)
	if phaaze_token == None:
		phaaze_token = _GET.get('phaaze_token', None)
	if phaaze_token == None:
		phaaze_token = request.headers.get('phaaze_token', None)

	if phaaze_token != None:
		return None
		# TODO: be able ti auth with token

	#via username and password
	phaaze_password = kwargs.get('password', None)
	if phaaze_password == None:
		phaaze_password = _POST.get('password', None)
	if phaaze_password == None:
		phaaze_password = _JSON.get('password', None)
	if phaaze_password == None:
		phaaze_password = _GET.get('password', None)

	phaaze_username = kwargs.get('username', None)
	if phaaze_username == None:
		phaaze_username = _POST.get('username', None)
	if phaaze_username == None:
		phaaze_username = _JSON.get('username', None)
	if phaaze_username == None:
		phaaze_username = _GET.get('username', None)

	if phaaze_username != None and phaaze_password != None:
		phaaze_password = self.password(phaaze_password)
		search_str = f"data['username'] == {json.dumps(phaaze_username)} and data['password'] == {json.dumps(phaaze_password)}"
		res = self.BASE.PhaazeDB.select(of="user", where=search_str)
		if len(res['data']) != 1:
			return None

		else:
			u = res['data'][0]
			res = self.BASE.PhaazeDB.select(of="role", where=f"int(data['id']) in {str(u.get('type', []))}")

			rl = []
			for role in res['data']:
				rl.append(role['name'])

			u['type'] = rl
			return u

	return None

#from string into password
def password(self, passwd):
	password = hashlib.sha256(passwd.encode("UTF-8")).hexdigest()
	return password

#generate a new sesssion key
def make_session_key(self):
	key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(16))
	return key

#check throw all roles and verify
def check_role(self, user_info, role):
	if user_info == None: return False

	if type(role) != list:
		role = [role]

	user_roles = user_info.get("role", [])
	user_roles = [u.lower() for u in user_roles]
	allowed_roles = [r.lower() for r in role]

	for ar in allowed_roles:
		if ar in user_roles: return True

	return False