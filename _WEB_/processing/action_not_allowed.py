#BASE.modules._Web_.Base.root.web.action_not_allowed

import html

async def main(self, request, msg=""):

	req_str = html.escape("Path: "+request.path)

	site = self.root.html_root
	user_info = await self.root.get_user_info(request)
	current_navbar = self.root.html_header(self.root.BASE, user_info=user_info)
	page_na = open('_WEB_/content/action_not_allowed.html', 'r').read()

	self.root.BASE.modules.Console.DEBUG(request.path)

	page_na = self.root.format_html(page_na,
		path=req_str,
		msg=msg
	)

	site = self.root.format_html(site,
		title="Phaaze | Not allowed",
		header=current_navbar,
		main=page_na
	)

	return self.root.response(
		body=site,
		status=403,
		content_type='text/html'
	)
