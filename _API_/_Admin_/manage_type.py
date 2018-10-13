import asyncio, json

# /api/admin/manage-type
async def main(self, request):

	method = request.match_info.get('method', 'get')

	if method == "get":
		return await get(self, request)

	elif method == "create":
		return await create(self, request)

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

	all_user = self.root.BASE.PhaazeDB.select(of="role")
	return self.root.response(
		body=json.dumps(all_user),
		status=200,
		content_type='application/json'
	)

async def create(self, request):

	user_info = await self.root.get_user_info(request)

	if user_info == None:
		return await self.action_not_allowed(request, msg="Login required")

	types = user_info.get("type", [])
	if not "admin" in [t.lower() for t in types]:
		return await self.action_not_allowed(request, msg="Admin rights reqired")

	_POST = await request.post()
	name = _POST.get('name', None)

	if name == None:
		return self.root.response(
			body=json.dumps(dict(status=400, msg="missing 'name' field")),
			status=400,
			content_type='application/json'
		)

	s_where = f"data['name'].lower() == {json.dumps(name)}.lower()"
	checkrole = self.root.BASE.PhaazeDB.select(of="role", where=s_where)
	if name.lower() in [role.get("name", "[N/A]").lower() for role in checkrole["data"]]:
		return self.root.response(
			body=json.dumps(dict(status=400, msg=f"role '{name}' already exists")),
			status=400,
			content_type='application/json'
		)

	# everything ok, create it
	new_role = dict( name=name, description=_POST.get("description", "").strip("\n") )
	self.root.BASE.PhaazeDB.insert(into="role", content=new_role)

	return self.root.response(
		body=json.dumps(dict(status=200, msg=f"role '{name}' successfull created")),
		status=200,
		content_type='application/json'
	)

async def update(self, request):
	pass

async def delete(self, request):
	pass