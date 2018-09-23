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
        return self.root.response()

async def get(self, request):
	_GET = request.query
	wl = []

	w_username = _GET.get('username', '')
	if w_username != "":
		w_username = w_username.replace("'", "\\'")
		wl.append( f"'{w_username}' in data['username']")

	w_type = _GET.get('type', '')
	if w_type != "":
		w_type = w_type.replace("'", "\\'")
		wl.append(f"'{w_type}' in data['type']")

	all_user = self.root.BASE.PhaazeDB.select(of="user", where=" and ".join(wl), fields=["username", "id", "type"])
	return self.root.response(
		body=json.dumps(all_user),
		status=200,
		content_type='application/json'
	)

async def update(self, request):
	pass

async def delete(self, request):
	pass