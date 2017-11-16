def page_not_found(BASE, info, dirs):
	page = open('_WEB_/content/page_not_found.html', 'r').read()

	page = page.replace("[[TEST]]", "MultiTestes")

	class r (object):
		content = page.encode('utf-8')
		response = 404
		header = [('Content-Type','text/html')]
	return r

