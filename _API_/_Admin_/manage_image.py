import asyncio, json, os, io
from PIL import Image

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
	limit = int(request.query.get("limit", "50")) if request.query.get("limit", "50").isdigit() else 50
	offset = int(request.query.get("offset", "0")) if request.query.get("offset", "0").isdigit() else 0

	files = []

	for f in os.listdir("_WEB_/img/"):
		if offset > 0: offset -= 1; continue
		if limit <= 0: break
		if f.endswith(".py") or (f.startswith("__") and f.endswith("__")): continue
		if not search_term in f: continue

		limit -= 1
		files.append(f)

	files = sorted(files)
	return self.root.response(
		body=json.dumps(dict(status=200, files=files)),
		status=200,
		content_type='application/json'
	)

async def upload(self, request):
	user_info = await self.root.get_user_info(request)

	if user_info == None:
		return await self.action_not_allowed(request, msg="Login required")

	if not self.root.check_role(user_info, ['image uploader','admin']):
		return await self.action_not_allowed(request, msg="Insufficient rights.")

	image_name = None
	image_file = None

	rm = await request.multipart()
	while not rm.at_eof():
		part = await rm.next()
		if part == None: continue

		if part.name == "name": image_name = await part.text()
		if part.name == "file": image_file = await part.read()

	if image_name == None or image_file == None:
		return self.root.response(
			body=json.dumps(dict(status=400, msg="missing field 'name' or 'file'")),
			status=400,
			content_type='application/json'
		)

	image_name = str(image_name).replace("..", "").replace("/", "").replace(" ", "_")

	if image_name in [None, ""]:
		return self.root.response(
			body=json.dumps(dict(status=400, msg="field 'name' is invalid")),
			status=400,
			content_type='application/json'
		)

	try:
		image_file = Image.open(io.BytesIO(image_file))
		image_file.save(f"{self.root.BASE.vars.IMAGE_PATH}{image_name}")
	except:
		return self.root.response(
			body=json.dumps(dict(status=400, msg="file is not a valid image file")),
			status=400,
			content_type='application/json'
		)

	return self.root.response(
		body=json.dumps(dict(status=200, msg=f"successfull saved as: '{image_name}'")),
		status=200,
		content_type='application/json'
	)

async def delete(self, request):
	pass
