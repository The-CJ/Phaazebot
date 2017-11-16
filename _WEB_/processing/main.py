def main(BASE, info, dirs):
	#main site
	if len(info['path']) == 0:
		return main_site(BASE, info)

	#icon
	elif info['path'][0] == 'favicon.ico':
		return get_favicon()

	#something with js
	elif info['path'][0] == 'js':
		info['path'].pop(0)
		return dirs.js.main(BASE, info, dirs)

	#leads to another site
	else:
		try:
			next_path = "_WEB_.processing.{0}".format(info['path'][0])
			info['path'].pop(0)
			eval('import ' + next_path + ' as next_file')
			return next_file.main(BASE, info, dirs)

		except:
			return dirs.page_not_found.page_not_found(BASE, info, dirs)

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
