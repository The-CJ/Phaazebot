#BASE.moduls._Web_.Base.root.about.main

from importlib import reload
import json, hashlib, random, string

def main(BASE, info, root):
	#/about
	if len(info['path']) == 0:
		return about(BASE, info)

	#leads to another site - /about/[something]
	else:
		try:
			next_file = "root.about.{0}.main.main".format(info['path'][0].lower())
			info['path'].pop(0)
			return eval(next_file+"(BASE, info, root)")

		except:
			return root.page_not_found.page_not_found(BASE, info, root)

def about(BASE, info):
	return_header = [('Content-Type','text/html')]

	site = open('_WEB_/content/about/root.html', 'r').read()
	site = site.replace("<!-- Navbar -->", BASE.moduls._Web_.Utils.get_navbar(active='about'))

	try:
		content = open('_WEB_/content/about/page_{}.html'.format(page_index), 'r').read()
	except:
		content = open('_WEB_/content/about/page_main.html', 'r').read()

	page_index = info.get('values', {}).get("page", "main")
	site = site.replace("<!-- about_content -->", content)

	class r (object):
		content = site.encode("UTF-8")
		response = 200
		header = return_header
	return r
