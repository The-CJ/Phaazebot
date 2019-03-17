
import asyncio, json
import hashlib, random, string

async def get_user_informations(self, request, **kwargs):
	if hasattr(request, "user_info"):
		self.BASE.modules.Console.DEBUG(f"Used stored infos: {str(request.user_info)}", require="api:debug")
		return request.user_info

	userI = await Auth(self.BASE, request, **kwargs).Base()
	request.user_info = userI
	return userI

class Auth(object):
	def __init__(self, BASE, request, **kwargs):
		self.BASE = BASE
		self.request = request
		self.kwargs = kwargs

		self.result = None

	async def Base(self):
		"""
		Auth should if possible avoid reading in POST content if not needed
 		All vars have the same Auth way:
			System -> header/cookies -> GET -> JSON -> POST
		"""

		self.result = await self.system()
		if self.result != None: return self.result

		self.result = await self.cookies()
		if self.result != None: return self.result

		self.result = await self.header()
		if self.result != None: return self.result

		self.result = await self.get()
		if self.result != None: return self.result

		# if still not autherised, now we need to touch the request body

		if self.request.headers.get("content-type", None) == "application/json":
			self.result = await self.json()
			if self.result != None: return self.result

		if self.request.headers.get("content-type", "").startswith("multipart/"):
			self.result = await self.multipart()
			if self.result != None: return self.result

		self.result = await self.post()
		if self.result != None: return self.result

		# No auth way got a valid result
		return None

	# gather

	async def system(self):
		phaaze_session = self.kwargs.get('phaaze_session', None)
		if phaaze_session != None:
			return await self.via_session(phaaze_session)

		phaaze_token = self.kwargs.get('phaaze_token', None)
		if phaaze_token != None:
			return await self.via_token(phaaze_token)

		phaaze_username = self.kwargs.get('username', None)
		phaaze_password = self.kwargs.get('password', None)
		if phaaze_username != None and phaaze_password != None:
			return await self.via_logindata(phaaze_username, phaaze_password)

	async def cookies(self):
		phaaze_session = self.request.cookies.get('phaaze_session', None)
		if phaaze_session != None:
			return await self.via_session(phaaze_session)

		phaaze_token = self.request.cookies.get('phaaze_token', None)
		if phaaze_token != None:
			return await self.via_token(phaaze_token)

		# this makes no sense, but ok
		phaaze_username = self.request.cookies.get('username', None)
		phaaze_password = self.request.cookies.get('password', None)
		if phaaze_username != None and phaaze_password != None:
			return await self.via_logindata(phaaze_username, phaaze_password)

	async def header(self):
		phaaze_session = self.request.headers.get('phaaze_session', None)
		if phaaze_session != None:
			return await self.via_session(phaaze_session)

		phaaze_token = self.request.headers.get('phaaze_token', None)
		if phaaze_token != None:
			return await self.via_token(phaaze_token)

		# this makes no sense, but ok
		phaaze_username = self.request.headers.get('username', None)
		phaaze_password = self.request.headers.get('password', None)
		if phaaze_username != None and phaaze_password != None:
			return await self.via_logindata(phaaze_username, phaaze_password)

	async def get(self):
		phaaze_session = self.request.query.get('phaaze_session', None)
		if phaaze_session != None:
			return await self.via_session(phaaze_session)

		phaaze_token = self.request.query.get('phaaze_token', None)
		if phaaze_token != None:
			return await self.via_token(phaaze_token)

		# this makes no sense, but ok
		phaaze_username = self.request.query.get('username', None)
		phaaze_password = self.request.query.get('password', None)
		if phaaze_username != None and phaaze_password != None:
			return await self.via_logindata(phaaze_username, phaaze_password)

	async def json(self):
		_JSON = await self.request.json()

		phaaze_session = _JSON.get('phaaze_session', None)
		if phaaze_session != None:
			return await self.via_session(phaaze_session)

		phaaze_token = _JSON.get('phaaze_token', None)
		if phaaze_token != None:
			return await self.via_token(phaaze_token)

		# this makes no sense, but ok
		phaaze_username = _JSON.get('username', None)
		phaaze_password = _JSON.get('password', None)
		if phaaze_username != None and phaaze_password != None:
			return await self.via_logindata(phaaze_username, phaaze_password)

	async def multipart(self):
		self.BASE.modules.Console.DEBUG("Someone tryed to auth with multipart content", require="web:debug")
		return None # TODO: add multipart include auth method

	async def post(self):
		_POST = await self.request.post()

		phaaze_session = _POST.get('phaaze_session', None)
		if phaaze_session != None:
			return await self.via_session(phaaze_session)

		phaaze_token = _POST.get('phaaze_token', None)
		if phaaze_token != None:
			return await self.via_token(phaaze_token)

		# this makes no sense, but ok
		phaaze_username = _POST.get('username', None)
		phaaze_password = _POST.get('password', None)
		if phaaze_username != None and phaaze_password != None:
			return await self.via_logindata(phaaze_username, phaaze_password)

	# checker

	async def via_session(self, phaaze_session):
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

		return None

	async def via_token(self, phaaze_token):
		self.BASE.modules.Console.DEBUG("someone tryed to auth via Token method", require="api:debug")
		return None #TODO: add token auth

	async def via_logindata(self, phaaze_username, phaaze_password):
		phaaze_password = password(None, phaaze_password)
		search_str = f"user['username'] == {json.dumps(phaaze_username)} and user['password'] == {json.dumps(phaaze_password)}"
		join_user_roles = dict(of="role", store="role", where="role['id'] in user['role']", fields=["name"])
		res = self.BASE.PhaazeDB.select(of="user", where=search_str, join=join_user_roles, store="user")

		user = res.get('data', [])
		if len(user) == 1:
			user = user[0]
			user['role'] = [r['name'] for r in user.get('role', []) if r.get('name', False)]
			return user

		return None

#get user infos
async def _get_user_informations(self, request, **kwargs):

	_GET = dict()
	_POST = dict()
	_JSON = dict()

	_GET = request.query

	_POST = await request.post()

	try: _JSON = await request.json()
	except: pass


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
		phaaze_token = request.headers.get('phaaze_token', None)
	if phaaze_token == None:
		phaaze_token = _POST.get('phaaze_token', None)
	if phaaze_token == None:
		phaaze_token = _JSON.get('phaaze_token', None)
	if phaaze_token == None:
		phaaze_token = _GET.get('phaaze_token', None)

	if phaaze_token != None:
		return None
		# TODO: be able to auth with token

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
		search_str = f"user['username'] == {json.dumps(phaaze_username)} and user['password'] == {json.dumps(phaaze_password)}"
		join_user_roles = dict(of="role", store="role", where="role['id'] in user['role']", fields=["name"])
		res = self.BASE.PhaazeDB.select(of="user", where=search_str, join=join_user_roles, store="user")

		user = res.get('data', [])
		if len(user) == 1:
			user = user[0]
			user['role'] = [r['name'] for r in user.get('role', []) if r.get('name', False)]
			return user

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