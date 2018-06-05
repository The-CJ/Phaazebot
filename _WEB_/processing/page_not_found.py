#BASE.modules._Web_.Base.root.page_not_found

import html

def main(self, request, msg=""):
	page = open('_WEB_/content/page_not_found.html', 'r').read()

	#page = self.BASE.modules._Web_.Utils.format_html_functions(self.BASE, page)

	save_str = html.escape("Not Found: "+request.path)
	page = page.replace("<!-- path -->", save_str)
	page = page.replace("<!-- msg -->", msg)

	return self.response(
		text=page,
		status=404,
		content_type='text/html'
	)
