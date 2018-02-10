#BASE.moduls._Web_.Base.root.wiki.main

from importlib import reload
import json, hashlib, random, string, html

def main(BASE, info, root):
	#/wiki
	if len(info['path']) == 0:
		return wiki(BASE, info)

	#leads to another site - /wiki/[something]
	else:
		return root.page_not_found.page_not_found(BASE, info, root)

def wiki(BASE, info):
	return_header = [('Content-Type','text/html')]

	site = open('_WEB_/content/wiki/root.html', 'r').read()
	site = site.replace("<!-- Navbar -->", BASE.moduls._Web_.Utils.get_navbar(active='wiki'))

	page_index = info.get('values', {}).get("page", "main")
	page_index = page_index.replace('..', '')
	if page_index.startswith('/'):
		page_index = " N/A"

	try:
		content = open('_WEB_/content/wiki/pages/{}.html'.format(page_index), 'r').read()
	except:
		content = open('_WEB_/content/wiki/not_found.html', 'r').read()
		content = content.replace("<!-- tryed_path -->", page_index)

	site = site.replace("<!-- about_content -->", content)

	class r (object):
		content = site.encode("UTF-8")
		response = 200
		header = return_header
	return r

