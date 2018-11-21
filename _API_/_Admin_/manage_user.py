import asyncio, json

# /api/admin/manage-user
async def main(self, request):
	method = request.match_info.get('method', 'get')

	if method == "get":
	 	return await get(self, request)

	elif method == "update":
		return await update(self, request)

	elif method == "delete":
		return await delete(self, request)

	elif method == "impersonate":
		return await impersonate(self, request)

	else:
		return self.root.response(
			body=json.dumps(dict(status=400, msg="missing method")),
			status=400,
			content_type='application/json'
		)

async def get(self, request):
	user_info = await self.root.get_user_info(request)

	if user_info == None:
		return await self.action_not_allowed(request, msg="Login required")

	if not self.root.check_role(user_info, 'admin'):
		return await self.action_not_allowed(request, msg="Admin rights reqired")

	_GET = request.query
	wl = []

	w_username = _GET.get('username', '')
	if w_username != "":
		wl.append( f"{json.dumps(w_username)}.lower() in data['username'].lower()")

	w_id = _GET.get('userid', '')
	if w_id != "":
		wl.append(f"str(data['id']) == {json.dumps(w_id)}")

	if bool(_GET.get("detail", 0)) == True:
		fields = None # None == all
	else:
		fields = ["username", "id", "type"]

	if _GET.get("verified", "0") == "1":
		wl.append("data['verified'] == True")
	else:
		wl.append("data['verified'] == False")

	all_user = self.root.BASE.PhaazeDB.select(of="user", where=" and ".join(wl), fields=fields)
	return self.root.response(
		body=json.dumps(all_user.get('data', [])),
		status=200,
		content_type='application/json'
	)

async def update(self, request):
	user_info = await self.root.get_user_info(request)

	if user_info == None:
		return await self.action_not_allowed(request, msg="Login required")

	if not self.root.check_role(user_info, 'admin'):
		return await self.action_not_allowed(request, msg="Admin rights reqired")

	_JSON = await request.json()
	user_id = _JSON.get('user_id', None)

	if user_id == None:
		return self.root.response(
			body=json.dumps(dict(status=400, msg="missing field 'user_id'")),
			status=400,
			content_type='application/json'
		)

	c = dict()

	for x in _JSON:
		if x == "user_id": continue
		c[x] = _JSON[x]

	res = self.root.BASE.PhaazeDB.update(of="user", where=f"int(data['id']) == int({json.dumps(user_id)})", content=c)

	if res['hits'] == 1:
		return self.root.response(
			body=json.dumps(dict(status=200, msg="Successfully updated user")),
			status=200,
			content_type='application/json'
		)

async def delete(self, request):
	pass

async def impersonate(self, request):
	user_info = await self.root.get_user_info(request)

	if user_info == None:
		return await self.action_not_allowed(request, msg="Login required")

	if not self.root.check_role(user_info, 'superadmin'):
		return await self.action_not_allowed(request, msg="Superdmin rights reqired")

	_POST = await request.post()
	i = _POST.get('user_id', None)

	current_session = request.headers.get('phaaze_session', None)
	if current_session == None:
		current_session = request.cookies.get('phaaze_session', None)

	c = dict(user_id=int(i))
	w = f"data['session'] == {json.dumps(current_session)}"
	res = self.root.BASE.PhaazeDB.update(of="session/phaaze", where=w, content=c)

	return self.root.response(
		body=json.dumps(dict(status=200, msg="changed user", d=res)),
		status=200,
		content_type='application/json'
	)


