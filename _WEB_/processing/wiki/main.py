#BASE.moduls._Web_.Base.root.wiki.main

from importlib import reload
import json, hashlib, random, string, html

def main(BASE, info, root):
	#/wiki
	if len(info['path']) == 0:
		return wiki(BASE, info)

	else:
		return root.page_not_found.page_not_found(BASE, info, root)

def wiki(BASE, info):
	return_header = [('Content-Type','text/html')]

	site = open('_WEB_/content/wiki/root.html', 'r', encoding='utf-8').read()

	page_index = info.get('values', {}).get("page", "main")
	page_index = page_index.replace('..', '')
	if page_index.startswith('/'):
		page_index = " N/A"

	try:
		content = open('_WEB_/content/wiki/pages/{}.html'.format(page_index), 'r', encoding='utf-8').read()
	except:
		content = open('_WEB_/content/wiki/not_found.html', 'r', encoding='utf-8').read()
		content = content.replace("<!-- tryed_path -->", page_index)

	site = site.replace("<!-- about_content -->", content)
	site = BASE.moduls._Web_.Utils.format_html_functions(BASE, site, infos = info)
	class r (object):
		content = site.encode("UTF-8")
		response = 200
		header = return_header
	return r

