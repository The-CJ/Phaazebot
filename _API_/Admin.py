#/api/admin/

import json, asyncio

from _API_._Admin import Files as files
from _API_._Admin import Shutdown as shutdown

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

async def eval_command(self, request):
	user_info = await self.root.get_user_info(request)

	if user_info == None:
		return await self.login(request, msg="Login required")

	types = user_info.get("type", [])
	if not "superadmin" in [t.lower() for t in types]:
		return await self.action_not_allowed(request, msg="Superadmin rights reqired")

	#get command from content
	_POST = await request.post()
	command = _POST.get('command', 'Missing_Conent')

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

