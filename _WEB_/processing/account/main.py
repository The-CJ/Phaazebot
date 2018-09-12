#BASE.modules._Web_.Base.root.account.main

# /login
async def login(self, request):
	current_navbar = self.root.html_header(self.root.BASE)

	main = open('_WEB_/content/account/account_login.html', 'r').read()

	site = self.root.html_root
	site = self.root.format_html( site, title="Phaaze | Account - Login", header=current_navbar, main=main )

	return self.root.response(
		body=site,
		status=200,
		content_type='text/html'
	)

# /account
async def account(self, request):
	user = await self.root.get_user_info(request)

	self.root.BASE.modules.Console.DEBUG(str(user))

	# need to login
	if user == None:
		return await self.root.web.login(request)