import asyncio, json

# /api/wiki
async def main(self, request):

	method = request.match_info.get('method', 'get')

	if method == "get":
		return await get(self, request)

	elif method == "save":
		return await save(self, request)

	#elif method == "delete":
	#	return await delete(self, request)

	else:
		return self.root.response(
			body=json.dumps(dict(status=400, msg="missing method")),
			status=400,
			content_type='application/json'
		)

async def get(self, request):
	_GET = request.query
	url_id = _GET.get("url_id", None)
	if url_id == None or url_id == "":
		return self.root.response(
			body=json.dumps(dict(status=400, msg="missing field 'url_id'")),
			status=400,
			content_type='application/json'
		)


	j = dict(of="user", limit=1, where="int(user['id']) == int(data['edited_by'])", store="user")
	page_res = self.root.BASE.PhaazeDB.select(of="wiki", where=f"data['url_id'] == {json.dumps(url_id)}", join=j)

	page = page_res.get("data", [])
	if len(page) == 0:
		return self.root.response(
			body=json.dumps(dict(status=400, msg="no page found")),
			status=400,
			content_type='application/json'
		)
	else:
		p = page[0]
		u = p.get("user", [])
		if len(u) == 0: u = dict()
		else: u = u[0]

		user = dict(
			username = u.get("username",None),
			img_url = u.get("img_url",None),
			id = u.get("id",None),
		)

		return_info = dict(
			content=p.get("content",None),
			created_at=p.get("created_at",None),
			edited_at=p.get("edited_at",None),
			id=p.get("id",None),
			tags=p.get("tags",None),
			url_id=p.get("url_id",None),
			user=user
		)
		return self.root.response(
			body=json.dumps(return_info),
			status=400,
			content_type='application/json'
		)

async def save(self, request):
	_POST = await request.post()
	url_id = _POST.get("url_id", None)
	tags = _POST.get("tags", None)
	content = _POST.get("content", None)

	if not (url_id != None and tags != None and content != None):
		return self.root.response(
			body=json.dumps(dict(status=400, msg="required fields: 'url_id', 'tags', 'content'")),
			status=400,
			content_type='application/json'
		)

	user_info = await self.root.get_user_info(request)
	if not self.root.check_role(user_info, ['superadmin', 'admin', 'wiki moderator']):
		return await self.root.api.action_not_allowed(request, msg="You don't have permissions to edit the wiki")
