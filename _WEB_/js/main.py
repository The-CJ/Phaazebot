import json

def main(BASE, info, dirs):
	print(info)
	if len(info['path']) == 0:
		class r(object):
			content = json.dumps(dict(error="no file define")).encode(encoding='utf_8')
			response = 400
			header = [('Content-Type', 'application/json')]
		return r

	path_str = "_WEB_/js/{0}".format(info['path'][0])
	path_str = path_str.replace('..','')
	try:
		js_file = open(path_str, 'rb').read()
		class r(object):
			content = js_file
			response = 200
			header = [('Content-Type', 'application/javascript')]
		return r

	#no file like this
	except:
		class r(object):
			content = json.dumps(dict(error="file not found", path=path_str.replace('_WEB_', ''))).encode(encoding='utf_8')
			response = 404
			header = [('Content-Type', 'application/json')]
		return r
