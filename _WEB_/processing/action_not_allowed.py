#BASE.modules._Web_.Base.root.web.action_not_allowed

import html

async def main(self, request, msg=""):

	req_str = html.escape("Path: "+request.path)

	site = self.root.html_root
	current_navbar = self.root.html_header(self.root.BASE)
	page_na = open('_WEB_/content/action_not_allowed.html', 'r').read()

	self.root.BASE.modules.Console.DEBUG(request.path)

	page_nf = self.root.format_html(page_na,
		path=req_str,
		msg=msg
	)

	site = self.root.format_html(site,
		title="Phaaze | Not allowed",
		header=current_navbar,
		main=page_nf
	)

	return self.root.response(
		body=site,
		status=404,
		content_type='text/html'
	)
