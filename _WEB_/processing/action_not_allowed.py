#BASE.modules._Web_.Base.root.action_not_allowed

import html

async def main(BASE, info, root):
	page = open('_WEB_/content/action_not_allowed.html', 'r').read()

	page = BASE.modules._Web_.Utils.format_html_functions(BASE, page, infos = info)

	save_str = html.escape(info['raw_path'])
	page = page.replace("<!-- path -->", save_str)

	class r (object):
		content = page.encode('utf-8')
		response = 403
		header = [('Content-Type','text/html')]
	return r
