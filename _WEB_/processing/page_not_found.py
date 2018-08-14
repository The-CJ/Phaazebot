#BASE.modules._Web_.Base.root.web.page_not_found

import html, asyncio

async def main(self, request, msg=""):
	page = open('_WEB_/content/page_not_found.html', 'r').read()

	save_str = html.escape("Not Found: "+request.path)
	current_navbar = self.root.format_html(self.root.BASE.modules._Web_.Utils.get_navbar(active=''))

	page = self.root.format_html(page, msg=msg, path=save_str, navbar=current_navbar)
	print(request.path)
	return self.root.response(
		text=page,
		status=404,
		content_type='text/html'
	)
