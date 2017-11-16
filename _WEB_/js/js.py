import json

def js(BASE, info, dirs):
	if len(info['path']) == 0:
		class r(object):
			content = json.dumps('{"error":"no file defined"}').encode(encoding='utf_8')
			response = 400
			header = [('Content-Type', 'application/json')]
		return r

	try:
		path_str = "_WEB_/js/{}.js".format(info['path'][0])
		js_file = open(path_str, 'rb').read()
		class r(object):
			content = js_file
			response = 200
			header = [('Content-Type', 'application/javascript')]
		return r

	#no file like this
	except:
		class r(object):
			content = json.dumps('{"error":"file not found"}').encode(encoding='utf_8')
			response = 404
			header = [('Content-Type', 'application/json')]
		return r
