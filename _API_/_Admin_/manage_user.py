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

	types = user_info.get("type", [])
	if not "admin" in [t.lower() for t in types]:
		return await self.action_not_allowed(request, msg="Admin rights reqired")

	_GET = request.query
	wl = []

	w_username = _GET.get('username', '')
	if w_username != "":
		wl.append( f"{json.dumps(w_username)}.lower() in data['username'].lower()")

	w_type = _GET.get('type', '')
	if w_type != "":
		wl.append(f"{json.dumps(w_type)}.lower() in data['type'].lower()")

	w_id = _GET.get('userid', '')
	if w_id != "":
		wl.append(f"str(data['id']) == {json.dumps(w_id)}")

	if bool(_GET.get("detail", 0)) == True:
		fields = None # None == all
	else:
		fields = ["username", "id", "type"]

	all_user = self.root.BASE.PhaazeDB.select(of="user", where=" and ".join(wl), fields=fields)
	return self.root.response(
		body=json.dumps(all_user),
		status=200,
		content_type='application/json'
	)

async def update(self, request):
	pass

async def delete(self, request):
	pass