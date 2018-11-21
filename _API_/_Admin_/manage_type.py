import asyncio, json

# /api/admin/manage-type
async def main(self, request):

	method = request.match_info.get('method', 'get')

	if method == "get":
		return await get(self, request)

	elif method == "create":
		return await create(self, request)

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

	if not self.root.check_role(user_info, 'admin'):
		return await self.action_not_allowed(request, msg="Admin rights reqired")

	all_user = self.root.BASE.PhaazeDB.select(of="role", fields=["id", "name", "description", "can_be_removed"])
	return self.root.response(
		body=json.dumps(all_user.get('data', [])),
		status=200,
		content_type='application/json'
	)

async def create(self, request):

	user_info = await self.root.get_user_info(request)

	if user_info == None:
		return await self.action_not_allowed(request, msg="Login required")

	if not self.root.check_role(user_info, 'admin'):
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
	new_role = dict( name=name, description=_POST.get("description", "").strip("\n"), can_be_removed=True )
	self.root.BASE.PhaazeDB.insert(into="role", content=new_role)

	return self.root.response(
		body=json.dumps(dict(status=200, msg=f"role '{name}' successfull created")),
		status=200,
		content_type='application/json'
	)

async def delete(self, request):

	user_info = await self.root.get_user_info(request)

	if user_info == None:
		return await self.action_not_allowed(request, msg="Login required")

	if not self.root.check_role(user_info, 'admin'):
		return await self.action_not_allowed(request, msg="Admin rights reqired")

	_POST = await request.post()
	role_id = _POST.get('role_id', "")

	if role_id == "" or not role_id.isdigit():
		return self.root.response(
			body=json.dumps(dict(status=400, msg="missing 'role_id' field")),
			status=400,
			content_type='application/json'
		)

	r = self.root.BASE.PhaazeDB.select(of="role", where=f"int(data['id']) == int({json.dumps(role_id)})")
	if not r.get('data', []):
		return self.root.response(
			body=json.dumps(dict(status=400, msg=f"could not found role ID: {role_id}")),
			status=400,
			content_type='application/json'
		)

	role = r['data'][0]

	if role.get("can_be_removed", False) == False:
		return self.root.response(
			body=json.dumps(dict(status=400, msg=f"'{role.get('name', 'N/A')}' is marked as non-removable")),
			status=400,
			content_type='application/json'
		)

	self.root.BASE.PhaazeDB.delete(of="role", where=f"int(data['id']) == int({json.dumps(role.get('id', None))})")

	return self.root.response(
		body=json.dumps(dict(status=200, msg=f"successfull deleted role '{role.get('name', 'N/A')}'")),
		status=200,
		content_type='application/json'
	)


