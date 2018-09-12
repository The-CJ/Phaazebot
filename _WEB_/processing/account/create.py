import asyncio

# /account/create
async def create(self, request):
	current_navbar = self.root.html_header(self.root.BASE)

	main = open('_WEB_/content/account/account_create.html', 'r').read()

	site = self.root.html_root
	site = self.root.format_html( site, title="Phaaze | Account - Create", header=current_navbar, main=main )

	return self.root.response(
		body=site,
		status=200,
		content_type='text/html'
	)

