#BASE.moduls._Web_.Base.root.account.main

def main(BASE, info):

	#no session -> login
	if info.get('user', None) == None:
		return account_login(BASE, info)
	else:
		return account_main(BASE, info)

def account_login(BASE, info):
	return_header = [('Content-Type','text/html')]
	site = open('_WEB_/content/account/account_login.html', 'r').read()

	site = BASE.moduls._Web_.Utils.format_html_functions(BASE, site)

	class r (object):
		content = site.encode("UTF-8")
		response = 200
		header = return_header
	return r

def account_main(BASE, info):
	return_header = [('Content-Type','text/html')]
	site = open('_WEB_/content/account/account_main.html', 'r').read()
	site = "<h1>Nope</h1>"

	site = BASE.moduls._Web_.Utils.format_html_functions(BASE, site)

	class r (object):
		content = site.encode("UTF-8")
		response = 200
		header = return_header
	return r

