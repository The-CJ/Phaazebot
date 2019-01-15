#/api/admin/

import json, asyncio, time

# /api/admin/eval_command
async def eval_command(self, request):
	user_info = await self.root.get_user_info(request)

	if user_info == None:
		return await self.action_not_allowed(request, msg="Login required")

	if not self.root.check_role(user_info, 'superadmin'):
		return await self.action_not_allowed(request, msg="Superadmin rights reqired")

	#get command from content
	_POST = await request.post()
	command = _POST.get('command', 'Missing_Content')

	try:
		res = eval(command)
	except Exception as Fail:
		res = Fail

	res = str(res)

	return self.root.response(
		body=json.dumps(dict(result=res, status="200")),
		status=200,
		content_type='application/json'
	)

# /api/admin/status
async def status(self, request):

	user_info = await self.root.get_user_info(request)

	if user_info == None:
		return await self.action_not_allowed(request, msg="Login required")

	if not self.root.check_role(user_info, 'admin'):
		return await self.action_not_allowed(request, msg="Admin rights reqired")

	res = dict()

	BASE = self.root.BASE

	#version
	res['version'] = BASE.version

	#uptime
	res['uptime'] = time.time() - BASE.uptime_var_1

	#module status
	res['module_status'] = dict()
	for module_status in [m for m in dir(BASE.active) if not m.startswith("__")]:
		res['module_status'][module_status] = getattr(BASE.active, module_status)

	# discord
	if BASE.discord == None or not BASE.is_ready.discord:
		res['discord'] = None
	else:
		res['discord'] = dict(
			servers = len(BASE.discord.servers),
			user=get_unique_discord_members(BASE.discord.servers),
			bot_id=BASE.discord.user.id,
			bot_name=BASE.discord.user.name,
			bot_discriminator=BASE.discord.user.discriminator,
			bot_avatar=BASE.discord.user.avatar_url
		)

	# twitch
	if BASE.twitch == None or not BASE.is_ready.twitch:
		res['twitch'] = None
	else:
		res['twitch'] = dict(
			bot_host=BASE.twitch.host,
			bot_name=BASE.twitch.nickname,
			bot_traffic=BASE.twitch.traffic,
			channel=len(BASE.twitch.channels),
		)

	return self.root.response(
		body=json.dumps(dict(result=res, status=200)),
		status=200,
		content_type='application/json'
	)

# /api/admin/controll
async def controll(self, request):
	user_info = await self.root.get_user_info(request)

	if user_info == None:
		return await self.action_not_allowed(request, msg="Login required")

	if not self.root.check_role(user_info, 'admin'):
		return await self.action_not_allowed(request, msg="Admin rights reqired")

	try:
		_POST = await request.json()
	except:
		_POST = await request.post()

	action = _POST.get("action", None)

	# module switch
	if action == "module":
		return await module_switch(self, _POST)

	elif action == "discord_avatar":
		return await discord_avatar(self, _POST)

	else:
		return self.root.response(
			body=json.dumps(dict(msg="no usable 'action' field.", status=400)),
			status=400,
			content_type='application/json'
		)

# /api/admin/controll {action:module}
async def module_switch(self, _POST):
	module = _POST.get('module', None)
	state = _POST.get("state", None)
	if state == None:
		return self.root.response(
			body=json.dumps(dict(error="module state switch requires a 'module' field and a 'state'.", status=400)),
			status=400,
			content_type='application/json'
		)
	setattr(self.root.BASE.active, module.lower(), state)
	return self.root.response(
		body=json.dumps(dict(msg=f"module {module} now: {state}", status=200)),
		status=200,
		content_type='application/json'
	)

# /api/admin/controll {action:discord_avatar}
async def discord_avatar(self, _POST):
	upload = _POST.get("file", None)

	if upload == None:
		return self.root.response(
			body=json.dumps(dict(msg="'avatar' field missing.", status=400)),
			status=400,
			content_type='application/json'
		)

	if not (self.root.BASE.is_ready.discord and self.root.BASE.discord != None) :
		return self.root.response(
			body=json.dumps(dict(msg="Discord Module not active/ready -> cant perform", status=400)),
			status=400,
			content_type='application/json'
		)

	c = getattr(upload, "file", None)

	if c == None:
		return self.root.response(
			body=json.dumps(dict(msg=f"avatar can't be empty", status=400)),
			status=400,
			content_type='application/json'
		)

	discord_reg = self.root.BASE.discord.edit_profile(avatar=upload.file.read())
	x = self.root.BASE.run_async(discord_reg, exc_loop = self.root.BASE.Discord_loop)

	if "discord.error" in str(x):
		return self.root.response(
			body=json.dumps(dict(msg=f"avatar change failed", status=400)),
			status=400,
			content_type='application/json'
		)

	return self.root.response(
		body=json.dumps(dict(msg=f"avatar changed", status=200)),
		status=200,
		content_type='application/json'
	)

def get_unique_discord_members(servers):
	a = []

	for server in servers:
		for member in server.members:
			if member.id not in a: a.append(member.id)

	return len(a)

