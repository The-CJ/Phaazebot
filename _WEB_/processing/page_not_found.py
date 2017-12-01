import html

def page_not_found(BASE, info, dirs):
	page = open('_WEB_/content/page_not_found.html', 'r').read()
	nav = open('_WEB_/content/navbar_content.html', 'r').read()

	page = page.replace("<!-- Navbar -->", nav)


	save_str = html.escape("Not Found: "+info['raw_path'])
	page = page.replace("<!-- path -->", save_str)

	class r (object):
		content = page.encode('utf-8')
		response = 404
		header = [('Content-Type','text/html')]
	return r

