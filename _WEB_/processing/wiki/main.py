#BASE.moduls._Web_.Base.root.wiki.main

from importlib import reload
import json, hashlib, random, string

def main(BASE, info, dirs):
	#/wiki
	if len(info['path']) == 0:
		return wiki(BASE, info)

	#leads to another site - /wiki/[something]
	else:
		try:
			next_file = "dirs.wiki.{0}.main.main".format(info['path'][0].lower())
			info['path'].pop(0)
			return eval(next_file+"(BASE, info, dirs)")

		except:
			return dirs.page_not_found.page_not_found(BASE, info, dirs)

def wiki(BASE, info):
	return_header = [('Content-Type','text/html')]

	site = open('_WEB_/content/wiki/root.html', 'r').read()
	site = site.replace("<!-- Navbar -->", BASE.moduls._Web_.Utils.get_navbar(active='wiki'))

	page_index = info.get('values', {}).get("page", "main")
	try:
		content = open('_WEB_/content/wiki/page_{}.html'.format(page_index), 'r').read()
	except:
		content = open('_WEB_/content/wiki/page_main.html', 'r').read()

	site = site.replace("<!-- about_content -->", content)

	class r (object):
		content = site.encode("UTF-8")
		response = 200
		header = return_header
	return r
