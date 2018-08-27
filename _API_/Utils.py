
import asyncio
import json, requests, hashlib, datetime, random, string

# log in/out
# /api/login
async def login(self, request, **kwargs):

	auth_user = await self.root.get_user_info(request)

	_POST = await request.post()
	if auth_user == None and (_POST.get('phaaze_username', None) == None or _POST.get('password', None) == None):
		return self.root.response(
			status=400,
			text=json.dumps( dict(error="missing_data", status=400, message="fields 'password' and 'phaaze_username' must be defined") ),
			content_type="application/json"
		)

	if auth_user == None:
		return self.response(
			status=404,
			text=json.dumps( dict(error="wrong_data", status=404, message="'password' or 'phaaze_username' could not be found") ),
			content_type="application/json"
			)

	new_session = self.root.make_session_key()

	entry = dict(session = new_session, user_id=auth_user['id'])
	self.root.BASE.PhaazeDB.insert(into="session/phaaze", content=entry)

	return self.root.response(
		text=json.dumps( dict(phaaze_session=new_session,status=200) ),
		content_type="application/json",
		status=200
	)

# /api/logout
async def logout(self, request, **kwargs):

	user = await self.root.get_user_info(request)

	if user == None:
		return self.response(
			text=json.dumps( dict(error='missing_session_key', status=400) ),
			content_type="application/json",
			status=400
		)

	res = self.root.BASE.PhaazeDB.delete(of="session/phaaze", where=f"data['session'] == '{session_key}'")

	if res['hits'] == 1:
		return self.response(
			text=json.dumps( dict(status=200) ),
			content_type="application/json",
			status=200
		)


#get user infos
async def get_user_informations(self, request, **kwargs):

	_GET = dict()
	_POST = dict()
	_JSON = dict()

	try:
		_GET = request.query
	except Exception as e:
		pass

	try:
		_POST = await request.post()
	except Exception as e:
		pass

	try:
		_JSON = await request.json()
	except Exception as e:
		pass

	# All vars have the same Auth way: Systemcall var -> POST -> JSON Content -> GET

	#via session
	phaaze_session = request.headers.get('phaaze_session', None)
	if phaaze_session != None:
		search_str = f'data["session"] == "{phaaze_session}" '
		res = self.BASE.PhaazeDB.select(of="session/phaaze", where=search_str)
		if len(res['data']) != 1:
			return None

		else:
			user_session = res['data'][0]

		uid = user_session.get('user_id',"0")
		search_str = f'int(data["id"]) == int({uid}) '
		res = self.BASE.PhaazeDB.select(of="user", where=search_str)
		if len(res['data']) != 1:
			return None

		else:
			return res['data'][0]

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

	phaaze_username = kwargs.get('phaaze_username', None)
	if phaaze_username == None:
		phaaze_username = _POST.get('phaaze_username', None)
	if phaaze_username == None:
		phaaze_username = _JSON.get('phaaze_username', None)
	if phaaze_username == None:
		phaaze_username = _GET.get('phaaze_username', None)

	if phaaze_username != None and phaaze_password != None:
		phaaze_password = password(phaaze_password)
		search_str = f"data['phaaze_username'] == '{phaaze_username}' and data['password'] == '{phaaze_password}'"
		res = self.BASE.PhaazeDB.select(of="user", where=search_str)
		if len(res['data']) != 1:
			return None

		else:
			return res['data'][0]

	return None

#from string into password
def password(passwd):
	password = hashlib.sha256(passwd.encode("UTF-8")).hexdigest()
	return password

#generate a new sesssion key
def make_session_key():
	snonce = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(8))
	stime = hashlib.sha1( str(datetime.datetime.now()).encode("UTF-8") + snonce ).hexdigest()

	key = str(stime)
	return key
