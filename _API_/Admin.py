#/api/admin/

import json, asyncio, time

# TODO: renew
def toggle_moduls(BASE, info={}, from_web=False, **kwargs):
	"""toggle main Moduls status"""
	session = info.get("cookies",{}).get("phaaze_session", None)
	admin = BASE.api.utils.get_phaaze_user(BASE, session=session)

	if admin.get('type', "").lower() == 'superadmin':
		module = info['values'].get('modul',None)
		if module == None: return

		if eval("BASE.active.{} == True".format(module)):
			setattr(BASE.active, module, False)
			sta = 'False'

		else:
			setattr(BASE.active, module, True)
			sta = 'True'

		class r (object):
			content = json.dumps(dict(status='success', msg='module `{}` now `{}`'.format(module, sta))).encode("UTF-8")
			response = 200
			header = [('Content-Type', 'application/json')]
		return r

	else:
		class r (object):
			content = json.dumps(dict(status='error', msg='unauthorised')).encode("UTF-8")
			response = 400
			header = [('Content-Type', 'application/json')]
		return r

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

	#uptime
	res['uptime'] = time.time() - BASE.uptime_var_1

	#module status
	res['module_status'] = dict()
	for module_status in [m for m in dir(BASE.active) if not m.startswith("__")]:
		res['module_status'][module_status] = getattr(BASE.active, module_status)

	# discord
	if BASE.discord == None:
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

	return self.root.response(
		body=json.dumps(dict(result=res, status=200)),
		status=200,
		content_type='application/json'
	)

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

	# module switch
	module = _POST.get('module', None)
	if module != None:
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





def get_unique_discord_members(servers):
	a = []

	for server in servers:
		for member in server.members:
			if member.id not in a: a.append(member.id)

	return len(a)

