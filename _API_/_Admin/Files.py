#/api/admin/fiels

import json, requests, hashlib, asyncio

def edit(BASE, info={}, from_web=False, **kwargs):
	if not from_web: return

	#start auth
	session = info.get("cookies",{}).get("phaaze_session", None)
	auth_key = info.get("values",{}).get("auth_key", None)

	admin = BASE.api.utils.get_phaaze_user(BASE, token=auth_key, session=session)
	if admin == None: admin = {}

	#end auth

	if admin.get('type', None) != 'superadmin':
		class r (object):
			content = json.dumps(dict(status='error', msg='unauthorised')).encode("UTF-8")
			response = 400
			header = [('Content-Type', 'application/json')]
		return r

	content = info['content']
	file = info['values'].get('file', None)
	if file == None:
		class r (object):
			content = json.dumps(dict(status='error', msg='no_file_path')).encode("UTF-8")
			response = 400
			header = [('Content-Type', 'application/json')]
		return r

	overwrite = open(file ,'wb')
	overwrite.write(content)
	overwrite.close()

	class r (object):
		content = json.dumps(dict(status='success', msg='edited')).encode("UTF-8")
		response = 200
		header = [('Content-Type', 'application/json')]
	return r
