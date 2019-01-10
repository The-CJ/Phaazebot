import asyncio, json, datetime

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
	url_id = _GET.get("url_id", "").lower()
	if url_id == None or url_id == "":
		return self.root.response(
			body=json.dumps(dict(status=400, msg="missing field 'url_id'")),
			status=400,
			content_type='application/json'
		)

	url_id = url_id.strip(" ").strip("/").strip("..").strip("\\").replace(" ","_")

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
			title=p.get("title",None),
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
	url_id = _POST.get("url_id", "").lower()
	title = _POST.get("title", "")
	tags = _POST.get("tags", None)
	content = _POST.get("content", None)

	if not (url_id != None and tags != None and content != None and title != None):
		return self.root.response(
			body=json.dumps(dict(status=400, msg="required fields: 'url_id', 'tags', 'content', 'title'")),
			status=400,
			content_type='application/json'
		)

	user_info = await self.root.get_user_info(request)
	if not self.root.check_role(user_info, ['superadmin', 'admin', 'wiki moderator']):
		return await self.root.api.action_not_allowed(request, msg="You don't have permissions to edit the wiki")

	url_id = url_id.strip(" ").strip("/").strip("..").strip("\\").replace(" ","_")

	#check if page exist
	page_res = self.root.BASE.PhaazeDB.select(of="wiki", where=f"data['url_id'] == {json.dumps(url_id)}")
	if page_res.get("hits", 0) == 0:
		new = True
	else:
		new = False

	if new:
		entry = dict(
			content=content,
			created_by=user_info.get("id", 0),
			created_at=str(datetime.datetime.now()),
			edited_by=user_info.get("id", 0),
			edited_at=str(datetime.datetime.now()),
			tags=tags.split(","),
			title=title,
			url_id=url_id
		)

		res = self.root.BASE.PhaazeDB.insert(into="wiki", content=entry)

	else:
		update = dict(
			content=content,
			edited_by=user_info.get("id", 0),
			edited_at=str(datetime.datetime.now()),
			tags=tags.split(","),
			title=title,
		)

		res = self.root.BASE.PhaazeDB.update(of="wiki", content=update, where=f"data['url_id'] == {json.dumps(url_id)}")

	if 200 <= res.get("code", 400) <= 299:
		return self.root.response(
			body=json.dumps(dict(status=200, msg=f"successfull {'created' if new else 'edited'} page: {url_id}")),
			status=200,
			content_type='application/json'
		)
	else:
		return self.root.response(
			body=json.dumps(dict(status=400, msg=f"error {'creating' if new else 'editing'} page: {url_id}")),
			status=400,
			content_type='application/json'
		)
