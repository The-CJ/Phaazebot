import asyncio, json, datetime
import Regex, re

# /api/account
async def main(self, request):
	method = request.match_info.get('method', 'get')

	if method == "get":
		return await get(self, request)

	elif method == "edit":
		return await edit(self, request)

	elif method == "create":
		return await create(self, request)

	elif method == "avatar":
		return await avatar(self, request)

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
	auth_user = await self.root.get_user_info(request)

	if auth_user == None:
		return self.root.response(
			status=400,
			text=json.dumps( dict(error="missing_authorisation", status=400) ),
			content_type="application/json"
		)

	_POST = await request.post()

	# get current password and check
	check_password = _POST.get("current_password", None)
	if check_password == None or auth_user.get("password", None) != self.root.password(check_password):
		return self.root.response(
			status=400,
			text=json.dumps( dict(error="current_password_wrong", msg="Current password is not current", status=400) ),
			content_type="application/json"
		)

	changed_email = False # if yes, reset valiated and send mail

	new_username = _POST.get("username", None)
	new_email = _POST.get("email", None)
	new_password = _POST.get("new_password", None)
	new_password2 = _POST.get("new_password2", None)

	need_to_update = dict()

	if new_password not in [None, ""] and self.root.password(new_password) != auth_user.get("password", new_password): # set new password
		if new_password != new_password2:
			return self.root.response(
				text=json.dumps( dict(error="unequal_passwords", status=400, msg="the passwords are not the same") ),
				content_type="application/json",
				status=400
			)
		if len(new_password) < 8:
			return self.root.response(
				text=json.dumps( dict(error="invalid_password", status=400, msg="the new password must be at least 8 chars long") ),
				content_type="application/json",
				status=400
			)

		need_to_update["password"] = self.root.password(new_password)

	if new_username not in [None, ""] and new_username != auth_user.get("username", new_password): # set username

		#check if username taken
		check_user = self.root.BASE.PhaazeDB.select(of="user", where=f"data['username'].lower() == {json.dumps(new_username)}.lower()")
		if check_user.get('hits', 1) != 0:
			return self.root.response(
				status=400,
				text=json.dumps( dict(error="account_taken", msg="username or email is taken", status=400) ),
				content_type="application/json"
			)

		need_to_update["username"] = new_username

	if new_email not in [None, ""] and new_email != auth_user.get("email", new_email): # set email
		if len(new_email) < 5 or re.match(Regex.is_email, new_email) == None:
			return self.root.response(
				text=json.dumps( dict(error="invalid_email", status=400, msg="email looks false") ),
				content_type="application/json",
				status=400
			)
		#check if email is taken
		check_user = self.root.BASE.PhaazeDB.select(of="user", where=f"data['email'].lower() == {json.dumps(new_email)}.lower()")
		if check_user.get('hits', 1) != 0:
			return self.root.response(
				status=400,
				text=json.dumps( dict(error="account_taken", msg="username or email is taken", status=400) ),
				content_type="application/json"
			)

		need_to_update["verified"] = False
		need_to_update["email"] = new_email
		changed_email = True

	if need_to_update == dict():
		return self.root.response(
			status=200,
			text=json.dumps( dict(error="no_action_taken", msg="Nothing has been changed", status=200) ),
			content_type="application/json"
		)

	# all done, save update
	self.root.BASE.modules.Console.DEBUG(f"Account edit {auth_user.get('id',0)}: {str(need_to_update)}", require="api:account")
	res = self.root.BASE.PhaazeDB.update(of="user", where=f"str(data['id']) == str({auth_user.get('id',0)})", content=need_to_update)
	if res.get("hits", 0) == 1:
		return self.root.response(
			status=200,
			text=json.dumps( dict(error="successfull_edited", msg="Your account has been successfull edited", status=200) ),
			content_type="application/json"
		)
	else:
		return self.root.response(
			status=500,
			text=json.dumps( dict(error="edit_failed", msg="Editing you account failed", status=500) ),
			content_type="application/json"
		)

# /api/account/avatar
async def avatar(self, request, **kwargs):
	auth_user = await self.root.get_user_info(request)

	if auth_user == None:
		return self.root.response(
			status=400,
			text=json.dumps( dict(error="missing_authorisation", status=400) ),
			content_type="application/json"
		)

	_POST = await request.post()

	if bool(_POST.get("remove", "")):
		u = dict(img_path=None)
		res = self.root.BASE.PhaazeDB.update(of="user", where=f"str(data['id']) == str({auth_user.get('id',0)})", content=u)
		# TODO: remove from local file
		if res.get("hits", 0) >= 1:
			return self.root.response(
				status=200,
				text=json.dumps( dict(error="avatar_removed", msg="Your avatar has been removed", status=200) ),
				content_type="application/json"
			)

	# TODO: save new image and get url

	return self.root.response(
		status=400,
		text=json.dumps( dict(error="not_avariable", msg="Setting avatar avariable soon", status=400) ),
		content_type="application/json"
	)

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
	if len(email) < 5 or re.match(Regex.is_email, email) == None:
		return self.root.response(
			text=json.dumps( dict(error="invalid_email", status=400, msg="email looks false") ),
			content_type="application/json",
			status=400
		)
	#check if username is taken
	check_user = self.root.BASE.PhaazeDB.select(of="user", where=f"data['username'].lower() == {json.dumps(username)}.lower() or data['email'].lower() == {json.dumps(email)}.lower()")
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

