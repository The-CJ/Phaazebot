import asyncio, json, os

# /api/admin/manage-image
async def main(self, request):

	method = request.match_info.get('method', 'get')

	if method == "get":
		return await get(self, request)

	elif method == "upload":
		return await upload(self, request)

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

	if not self.root.check_role(user_info, ['image uploader','admin']):
		return await self.action_not_allowed(request, msg="Insufficient rights.")

	search_term = request.query.get("image", "")
	limit = int(request.query.get("limit", 50)) if request.query.get("limit", 50).isdigit() else 50
	offset = int(request.query.get("offset", 0)) if request.query.get("offset", 0).isdigit() else 0

	files = []

	for f in os.listdir("_WEB_/img/"):
		if offset > 0: offset -= 1; continue
		if limit <= 0: break
		if f.endswith(".py") or (f.startswith("__") and f.endswith("__")): continue
		if not search_term in f: continue

		limit -= 1
		files.append(f)

	return self.root.response(
		body=json.dumps(dict(status=200, files=files)),
		status=200,
		content_type='application/json'
	)

async def upload(self, request):
	pass

async def delete(self, request):
	pass
