import json, mimetypes

def main(BASE, info, dirs):
	if len(info['path']) == 0:
		class r(object):
			content = json.dumps(dict(error="no file define")).encode(encoding='utf_8')
			response = 400
			header = [('Content-Type', 'application/json')]
		return r

	path_str = "_WEB_/img/{0}".format(info['path'][0])
	path_str = path_str.replace('..','')
	try:
		js_file = open(path_str, 'rb').read()
		cont_type = mimetypes.guess_type(path_str, strict=True)
		print(cont_type)
		class r(object):
			content = js_file
			response = 200
			header = [('Content-Type', cont_type[0])]
		return r

	#no file like this
	except:
		class r(object):
			content = json.dumps(dict(error="file not found", path=info['raw_path'])).encode(encoding='utf_8')
			response = 404
			header = [('Content-Type', 'application/json')]
		return r
