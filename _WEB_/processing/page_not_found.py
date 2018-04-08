#BASE.moduls._Web_.Base.root.page_not_found

import html

def page_not_found(BASE, info, root, msg=""):
	page = open('_WEB_/content/page_not_found.html', 'r').read()

	page = BASE.moduls._Web_.Utils.format_html_functions(BASE, page, infos = info)

	save_str = html.escape("Not Found: "+info['raw_path'])
	page = page.replace("<!-- path -->", save_str)
	page = page.replace("<!-- msg -->", msg)

	class r (object):
		content = page.encode('utf-8')
		response = 404
		header = [('Content-Type','text/html')]
	return r

