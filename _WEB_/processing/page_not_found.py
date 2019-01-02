#BASE.modules._Web_.Base.root.web.page_not_found

import html, asyncio

async def main(self, request, msg=""):

	req_str = html.escape("Not Found: "+request.path)

	site = self.root.html_root
	user_info = await self.root.get_user_info(request)
	current_navbar = self.root.html_header(self.root.BASE, user_info=user_info)
	page_nf = open('_WEB_/content/page_not_found.html', 'r').read()

	self.root.BASE.modules.Console.DEBUG(f"404: {request.path}", require="web:404")

	page_nf = self.root.format_html(page_nf,
		path=req_str,
		msg=msg
	)

	site = self.root.format_html(site,
		title="Phaaze | Not Found",
		header=current_navbar,
		main=page_nf
	)

	return self.root.response(
		body=site,
		status=404,
		content_type='text/html'
	)
