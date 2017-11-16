def main(BASE, info, dirs):
	#main site
	if len(info['path']) == 0:
		return main_site(BASE, info)

	elif info['path'][0] == 'favicon.ico':
		return get_favicon()

	elif info['path'][0] == 'js':
		info['path'].pop(0)
		return dirs.js.js(BASE, info, dirs)

def main_site(BASE, info):
	class r (object):
		content = open('_WEB_/content/main.html', 'rb').read()
		response = 200
		header = [('Content-Type','text/html')]
	return r

def get_favicon():
	class r (object):
		content = open('_WEB_/content/favicon.ico', 'rb').read()
		response = 200
		header = [('Content-Type','image/x-icon')]
	return r
