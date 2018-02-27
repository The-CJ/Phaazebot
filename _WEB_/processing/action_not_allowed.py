#BASE.moduls._Web_.Base.root.action_not_allowed

import html

def action_not_allowed(BASE, info, root):
	page = open('_WEB_/content/action_not_allowed.html', 'r').read()

	page = page.replace("<!-- Navbar -->", BASE.moduls._Web_.Utils.get_navbar(active=''))


	save_str = html.escape(info['raw_path'])
	page = page.replace("<!-- path -->", save_str)

	class r (object):
		content = page.encode('utf-8')
		response = 403
		header = [('Content-Type','text/html')]
	return r

