
import asyncio, json
import hashlib, datetime, random, string

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
		search_str = f'data["session"] == {json.dumps(phaaze_session)}'
		res = self.BASE.PhaazeDB.select(of="session/phaaze", where=search_str)
		if len(res['data']) == 1:
			user_session = res['data'][0]

			uid = user_session.get('user_id',"0")
			search_str = f"int(data['id']) == int({uid})"
			res = self.BASE.PhaazeDB.select(of="user", where=search_str)
			if len(res['data']) == 1:
				return_user = res['data'][0]

				search_str = f"int(data['id']) in {str(return_user.get('type',[]))}"
				res = self.BASE.PhaazeDB.select(of="role", where=search_str)

				rl = []
				for role in res['data']:
					rl.append(role['name'])

				return_user['type'] = rl
				return return_user

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
