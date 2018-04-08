import json
import traceback
import _API_.Utils as utils

												################################
												#          API Paths           #
												################################
from _API_.Utils import login as login			# /api/login
from _API_.Utils import logout as logout		# /api/logout
												#
import _API_.Admin as admin						#------------------------------#
												# /api/admin/toggle_moduls
												# /api/admin/eval_command
												# /api/admin/fiels/edit
												# /api/admin/shutdown/api
												# /api/admin/shutdown/web
												#
import _API_.Discord as discord					#------------------------------#
												# /api/discord/login
												# /api/discord/logout
												# /api/discord/get_servers
												# /api/discord/custom/get
												# /api/discord/custom/delete
												#
import _API_.DataBase as db						#------------------------------#
												#
												#
												#
												#
												#
												#


def call(BASE, web_info):
	"""
	used to process api calls from the web, comming in a /api/[module]/[function] scheme

	all function are also accessable via BASE.api.[module].[function]()
	"""

	if not BASE.active.api:
		class r (object):
			content = json.dumps(dict(status="error", msg="api_endpoint_closed")).encode("UTF-8")
			response = 403
			header = [('Content-Type', 'application/json')]
		return r

	web_info['path'].pop(0)

	if len(web_info['path']) == 0:
		class r (object):
			content = json.dumps(dict(status="error", msg="no_path", _m="Trying to find out the PhaazeAPI?. Try looking at phaaze.net/wiki?page=api")).encode("UTF-8")
			response = 400
			header = [('Content-Type', 'application/json')]
		return r

	function_call = ".".join(step for step in web_info['path'])
	function_call = "BASE.api." + function_call + "(BASE, info=web_info, from_web=True)"

	try:
		return eval(function_call)
	except:
		traceback.print_exc()

		class r (object):
			content = json.dumps(dict(status="error", msg="not_found")).encode("UTF-8")
			response = 400
			header = [('Content-Type', 'application/json')]
		return r
