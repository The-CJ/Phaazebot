#/api/admin/shutdown

import json, requests, hashlib, asyncio

def api(BASE, info={}, from_web=False, **kwargs):
	if not from_web: return

	#start auth
	session = info.get("cookies",{}).get("phaaze_session", None)
	auth_key = info.get("values",{}).get("auth_key", None)

	admin = BASE.api.utils.get_phaaze_user(BASE, api_token=auth_key, session=session)
	if admin == None: admin = {}

	#end auth

	if admin.get('type', "").lower() != 'superadmin':
		class r (object):
			content = json.dumps(dict(status='error', msg='unauthorised')).encode("UTF-8")
			response = 400
			header = [('Content-Type', 'application/json')]
		return r

	time = int(info.get("values",{}).get("time", 5))

	async def timeout(BASE, t ):
		BASE.modules.Console.WARNING("API Disabled for " + str(time) + " min")
		BASE.active.api = False
		await asyncio.sleep(t*60)
		BASE.active.api = True
		BASE.modules.Console.WARNING("API timeout over -> Starting")

	asyncio.ensure_future(timeout(BASE, time), loop=BASE.Worker_loop)
	class r (object):
		content = json.dumps(dict(status='success', msg='shutting down')).encode("UTF-8")
		response = 200
		header = [('Content-Type', 'application/json')]
	return r

def web(BASE, info={}, from_web=False, **kwargs):
	if not from_web: return

	#start auth
	session = info.get("cookies",{}).get("phaaze_session", None)
	auth_key = info.get("values",{}).get("auth_key", None)

	admin = BASE.api.utils.get_phaaze_user(BASE, api_token=auth_key, session=session)
	if admin == None: admin = {}

	#end auth

	if admin.get('type', "").lower() != 'superadmin':
		class r (object):
			content = json.dumps(dict(status='error', msg='unauthorised')).encode("UTF-8")
			response = 400
			header = [('Content-Type', 'application/json')]
		return r

	time = int(info.get("values",{}).get("time", 5))

	async def timeout(BASE, t ):
		BASE.modules.Console.WARNING("Main Web Disabled for " + str(time) + " min")
		BASE.active.web = False
		await asyncio.sleep(t*60)
		BASE.active.web = True
		BASE.modules.Console.WARNING("Main Web timeout over -> Starting")

	asyncio.ensure_future(timeout(BASE, time), loop=BASE.Worker_loop)
	class r (object):
		content = json.dumps(dict(status='success', msg='shutting down')).encode("UTF-8")
		response = 200
		header = [('Content-Type', 'application/json')]
	return r
