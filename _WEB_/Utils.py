import re

def get_navbar(BASE, active=''):
	navbar = open('_WEB_/content/_navbar/navbar_content.html', 'r').read()
	if active != '':
		try:
			addition = open(f'_WEB_/content/_navbar/navbar_content_{active}.html', 'r').read()
			navbar = navbar + addition
		except:
			pass

		# remove active selector
		ac = re.finditer(r'\{selected_(.+)\}', navbar)
		for c in ac:
			if c.group(1) == active:
				navbar = navbar.replace(c.group(0), 'active')
			else:
				navbar = navbar.replace(c.group(0), '')

	navbar_login = get_login_btn(BASE)

	navbar = navbar.replace('|>>>(navbar_login)<<<|', navbar_login)

	return navbar

def get_login_btn(BASE, **kwargs):
	if kwargs.get('platform', None) != None:
		pass

	if kwargs.get('user', None) == None:
		no_login = open('_WEB_/content/_buttons/no_login.html', 'r').read()
		return no_login
	else:
		main_btn = open('_WEB_/content/_buttons/phaaze_login.html', 'r').read()
		main_btn = main_btn.replace('{name}', kwargs.get('user', {}).get('phaaze_username', '[NAME N/A]'))
		main_btn = main_btn.replace('{type}', kwargs.get('user', {}).get('type', '[TYPE N/A]'))
		if kwargs.get('user', {}).get('img_path', None) != None:
			img = 'HELLO'
		else:
			img = 'hidden'
		main_btn = main_btn.replace('{img_path}', img)
		return main_btn

def format_html(self, html_string, **values):
	"""
	This function will take all
	|>>>(kwarg)<<<|
	in the .html, and replace kwarg with the right key match from **values
	else empty string

	returns formated html
	"""
	search_results = re.finditer(self.format_html_regex, html_string)
	for hit in search_results:
		rep = values.get(hit.group(1), "")
		html_string = html_string.replace(hit.group(0), rep)

	return html_string


