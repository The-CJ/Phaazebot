import asyncio, json, datetime

async def main(self, request):
	method = request.match_info.get('method', 'get')

	if method == "get":
		return await get(self, request)

	elif method == "edit":
		return await edit(self, request)

	elif method == "create":
		return await create(self, request)

	elif method == "login":
		return await login(self, request)

	elif method == "logout":
		return await logout(self, request)

	else:
		return self.root.response(
			status=400,
			text=json.dumps( dict(error="invalid_method", status=400) ),
			content_type="application/json"
		)

# /api/account/get
async def get(self, request, **kwargs):

	auth_user = await self.root.get_user_info(request)

	if auth_user == None:
		return self.root.response(
			status=400,
			text=json.dumps( dict(error="missing_authorisation", status=400) ),
			content_type="application/json"
		)

	if auth_user.get("password", None) != None: del auth_user["password"]
	return self.root.response(
		status=200,
		text=json.dumps(auth_user),
		content_type="application/json"
	)

# /api/account/edit
async def edit(self, request, **kwargs):
	pass

# /api/account/login
async def login(self, request, **kwargs):

	auth_user = await self.root.get_user_info(request)

	_POST = await request.post()
	if auth_user == None and (_POST.get('username', None) in [None, ""] or _POST.get('password', None) in [None, ""]):
		return self.root.response(
			status=400,
			text=json.dumps( dict(error="missing_data", status=400, message="fields 'password' and 'username' must be defined") ),
			content_type="application/json"
		)

	if auth_user == None:
		return self.root.response(
			status=404,
			text=json.dumps( dict(error="wrong_data", status=404, message="'password' or 'username' could not be found") ),
			content_type="application/json"
			)

	new_session = self.root.make_session_key()

	entry = dict(session = new_session, user_id=auth_user['id'])
	self.root.BASE.PhaazeDB.insert(into="session/phaaze", content=entry)
	self.root.BASE.PhaazeDB.update(of="user", content=dict(last_login=str(datetime.datetime.now())), where=f"int(data['id']) == int({entry.get('user_id', None)})")
	self.root.BASE.modules.Console.DEBUG(f"New Login - Session: {new_session}\n{str(auth_user)}", require="api:login")
	return self.root.response(
		text=json.dumps( dict(phaaze_session=new_session,status=200) ),
		content_type="application/json",
		status=200
	)

# /api/account/logout
async def logout(self, request, **kwargs):

	user = await self.root.get_user_info(request)

	if user == None:
		return self.root.response(
			text=json.dumps( dict(error='missing_session_key', status=400) ),
			content_type="application/json",
			status=400
		)

	us_id = user.get('id', '')
	res = self.root.BASE.PhaazeDB.delete(of="session/phaaze", where=f"int(data['user_id']) == int({us_id})")
	self.root.BASE.modules.Console.DEBUG(f"Logout of user: {str(us_id)}", require="api:logout")
	if res['hits'] >= 1:
		return self.root.response(
			text=json.dumps( dict(status=200) ),
			content_type="application/json",
			status=200
		)

# /api/account/create
async def create(self, request, **kwargs):
	auth_user = await self.root.get_user_info(request)
	if auth_user != None:
		return self.root.response(
			text=json.dumps( dict(error="aleady_logged_in", status=400, msg="no registion needed, already logged in") ),
			content_type="application/json",
			status=400
		)

	_POST = await request.post()

	username = _POST.get('username', None)
	email = _POST.get('email', None)
	password = _POST.get('password', None)
	password2 = _POST.get('password2', None)

	#check all things that don't require db request's

	#password
	if password != password2:
		return self.root.response(
			text=json.dumps( dict(error="unequal_passwords", status=400, msg="the passwords are not the same") ),
			content_type="application/json",
			status=400
		)
	if len(password) < 8:
		return self.root.response(
			text=json.dumps( dict(error="invalid_password", status=400, msg="the password must be at least 8 chars long") ),
			content_type="application/json",
			status=400
		)
	#email
	if len(email) < 5:
		return self.root.response(
			text=json.dumps( dict(error="invalid_email", status=400, msg="email looks false") ),
			content_type="application/json",
			status=400
		)
	#check if username is taken
	check_user = self.root.BASE.PhaazeDB.select(of="user", where=f"data['username'] == {json.dumps(username)} or data['email'] == {json.dumps(email)}")
	if check_user.get('hits', 1) != 0:
		self.root.BASE.modules.Console.DEBUG(f"User already exist: {str(auth_user)}", require="api:create")
		return self.root.response(
			text=json.dumps( dict(error="account_taken", status=400, msg="username or email is taken") ),
			content_type="application/json",
			status=400
		)

	passwd = self.root.password(password)

	cont = dict(
		username=username,
		password=passwd,
		email=email,
		verified=False,
		img_path=None,
		last_login=None,
		type=[]
	)

	#TODO: need to send email verification

	new_user = self.root.BASE.PhaazeDB.insert(into="user", content=cont)
	_id_ = new_user.get('data', {}).get('id', '[N/A]')

	self.root.BASE.modules.Console.DEBUG(f"User created: {str(cont)}", require="api:create")
	return self.root.response(
		text=json.dumps( dict(status=200, message="successfull created user", id=_id_, username=username) ),
		content_type="application/json",
		status=200
	)

