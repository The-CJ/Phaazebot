#/api/admin/

import json

from _API_._Admin import Files as files
from _API_._Admin import Shutdown as shutdown

def toggle_moduls(BASE, info={}, from_web=False, **kwargs):
	"""toggle main Moduls status"""
	session = info.get("cookies",{}).get("phaaze_session", None)
	admin = BASE.api.utils.get_phaaze_user(BASE, session=session)
	
	if admin.get('type', None) == 'superadmin':
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

def eval_command(BASE, info={}, from_web=False, **kwargs):
	if not from_web: return

	#start auth
	session = info.get("cookies",{}).get("admin_session", None)
	auth_key = info.get("values",{}).get("auth_key", None)
	username = info.get("values",{}).get("username", None)
	passwd = info.get("values",{}).get("passwords", None)

	admin = BASE.api.utils.authorise_admin(BASE, session=session, auth_key=auth_key, username=username, password=passwd)
	if admin == None: admin = {}

	#end auth

	if admin.get('type', None) != 'superadmin':
		class r (object):
			content = json.dumps(dict(status='error', msg='unauthorised')).encode("UTF-8")
			response = 400
			header = [('Content-Type', 'application/json')]
		return r

	#get command from content
	command = json.loads(info.get('content', {})).get('command', 'Missing_Conent')

	try:
		res = eval(command)
	except Exception as Fail:
		res = Fail

	res = str(res)

	class r (object):
		content = json.dumps(dict(status='success', result=res)).encode("UTF-8")
		response = 200
		header = [('Content-Type', 'application/json')]
	return r
