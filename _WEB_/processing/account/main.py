#BASE.modules._Web_.Base.root.account.main

# /login
async def login(self, request):
	user_info = await self.root.get_user_info(request)
	# already is logged in
	if user_info != None:
		return self.root.response(
			status=307,
			headers=dict(location="/account")
		)

	current_navbar = self.root.html_header(self.root.BASE, user_info=user_info)

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
	user_info = await self.root.get_user_info(request)

	# need to login
	if user_info == None:
		return await self.root.web.login(request)

	current_navbar = self.root.html_header(self.root.BASE, user_info=user_info)
	main = open('_WEB_/content/account/account_main.html', 'r').read()

	site = self.root.html_root
	site = self.root.format_html( site, title="Phaaze | Account - Login", header=current_navbar, main=main )

	return self.root.response(
		body=site,
		status=200,
		content_type='text/html'
	)

