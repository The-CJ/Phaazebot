# /api/custom/<x>

import json, requests, discord, asyncio, hashlib

def get(BASE, info={}, from_web=False, **kwargs):
	"""Out Only"""

	server_id = kwargs.get('id', None)
	if server_id == None:
		server_id = info.get('values', {}).get('id', None)
	if server_id == None:
		try:
			con = json.loads(info.get('content', ""))
			server_id = con.get('id', None)
		except Exception as e:
			pass

	if server_id == None:
		if from_web:
			class r (object):
				content = json.dumps(dict(status='error', msg="missing 'id' field")).encode("UTF-8")
				response = 400
				header = [('Content-Type', 'application/json')]
			return r
		else:
			raise AttributeError("missing 'id' value")


	x = BASE.modules.Utils.get_server_file(BASE, server_id, prevent_new=True)
	save_settings = BASE.call_from_async(x ,BASE.Discord_loop)

	if save_settings == None: save_settings = {}

	all_commands = save_settings.get('commands', [])

	if from_web:
		class r (object):
			content = json.dumps(dict(status='success', data=all_commands)).encode("UTF-8")
			response = 200
			header = [('Content-Type', 'application/json')]
		return r
	else:
		raise all_commands

def delet(BASE, info={}, from_web=False, **kwargs):

	#get vars
	server_id = kwargs.get('server_id', None)
	trigger = kwargs.get('trigger', None)

	if server_id == None or trigger == None:
		server_id = info.get('values', {}).get('server_id', None)
		server_id = info.get('values', {}).get('trigger', None)

	if server_id == None or trigger == None:
		try:
			con = json.loads(info.get('content', ""))
			server_id = con.get('server_id', None)
			trigger = con.get('trigger', None)
		except Exception as e:
			pass

	if server_id == None or trigger == None:
		if from_web:
			class r (object):
				content = json.dumps(dict(status='error', msg="missing 'server_id' or 'trigger' field")).encode("UTF-8")
				response = 400
				header = [('Content-Type', 'application/json')]
			return r
		else:
			raise AttributeError("missing 'server_id' or 'trigger' value")

	#auth
	auth = False
	if not from_web: #intern call
		auth = True

	if not auth: #call from outside, need auth

		session = info['cookies'].get('discord_session', None)
		discord_user = BASE.api.utils.get_discord_user_by_session(BASE, session)

		try:
			discord_server = BASE.discord.get_server(server_id)
			discord_member = discord_server.get_member(discord_user.get('user_info', {}).get('id', None) )
			perm = discord_member.server_permissions
			if perm.manage_server or perm.administrator:
				auth = True
		except:
			pass

	if not auth: # not authorized
		class r (object):
			content = json.dumps(dict(status='error', msg="unauthorized")).encode("UTF-8")
			response = 402
			header = [('Content-Type', 'application/json')]
		return r

	#get server file
	x = BASE.modules.Utils.get_server_file(BASE, server_id, prevent_new=True)
	save_settings = BASE.run_async(x ,BASE.Discord_loop)

	#get command -> delete
	found = False
	for cmd in save_settings.get('commands',[]):
		if cmd['trigger'] == trigger:
			save_settings['commands'].remove(cmd)
			found = True

	#non found
	if not found:
		if from_web:
			class r (object):
				content = json.dumps(dict(status='error', msg="no command with trigger: '{}'".format(trigger))).encode("UTF-8")
				response = 400
				header = [('Content-Type', 'application/json')]
			return r
		else:
			raise AttributeError("no command found with: "+trigger)

	#finish
	with open("SERVERFILES/{0}.json".format(server_id), "w") as save:
		json.dump(save_settings, save)
		setattr(BASE.serverfiles, "server_"+server_id, save_settings)

		if from_web:
			class r (object):
				content = json.dumps(dict(status='success', msg="command: '{}' deleted".format(trigger))).encode("UTF-8")
				response = 200
				header = [('Content-Type', 'application/json')]
			return r
		else:
			return True
