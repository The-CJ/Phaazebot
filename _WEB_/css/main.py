import json

def main(BASE, info, dirs):
	if len(info['path']) == 0:
		class r(object):
			content = json.dumps(dict(error="no file define")).encode(encoding='utf_8')
			response = 400
			header = [('Content-Type', 'application/json')]
		return r

	path_str = "_WEB_/css/{0}".format(info['path'][0])
	path_str = path_str.replace('..','')
	try:
		js_file = open(path_str, 'rb').read()
		if path_str.endswith(".py"):
			class r(object):
				content = json.dumps(dict(error="not_allowed"))
				response = 403
				header = [('Content-Type', 'text/json')]
			return r
		class r(object):
			content = js_file
			response = 200
			header = [('Content-Type', 'text/css')]
		return r

	#no file like this
	except:
		class r(object):
			content = json.dumps(dict(error="file not found", path=info['raw_path'])).encode(encoding='utf_8')
			response = 404
			header = [('Content-Type', 'application/json')]
		return r
