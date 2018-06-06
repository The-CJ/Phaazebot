#BASE.modules._Web_.Base.root.page_not_found

import html

async def main(self, request, msg=""):
	page = open('_WEB_/content/page_not_found.html', 'r').read()

	save_str = html.escape("Not Found: "+request.path)
	current_navbar = self.format_html(self.BASE.modules._Web_.Utils.get_navbar(active=''))

	page = self.format_html(page, msg=msg, path=save_str, navbar=current_navbar)

	return self.response(
		text=page,
		status=404,
		content_type='text/html'
	)
