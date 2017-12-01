#BASE.moduls._Web_.Base.root.main

from importlib import reload
import traceback

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

	#something with js
	elif info['path'][0] == 'css':
		info['path'].pop(0)
		return dirs.css.main(BASE, info, dirs)

	#some image
	elif info['path'][0] == 'img':
		info['path'].pop(0)
		return dirs.img.main(BASE, info, dirs)

	#leads to another site
	else:
		try:
			next_file = "dirs.{0}.main.main".format(info['path'][0].lower())
			info['path'].pop(0)
			return eval(next_file+"(BASE, info, dirs)")

		except:
			print(traceback.format_exc())
			return dirs.page_not_found.page_not_found(BASE, info, dirs)

def main_site(BASE, info):
	site = open('_WEB_/content/main.html', 'r').read()
	nav = open('_WEB_/content/navbar_content.html', 'r').read()

	site = site.replace("<!-- Navbar -->", nav)


	class r (object):
		content = site.encode("UTF-8")
		response = 200
		header = [('Content-Type','text/html')]
	return r

def get_favicon():
	class r (object):
		content = open('_WEB_/content/favicon.ico', 'rb').read()
		response = 200
		header = [('Content-Type','image/x-icon')]
	return r
