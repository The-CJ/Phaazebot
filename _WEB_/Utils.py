#BASE.modules._Web_.Utils

import re

def get_navbar(active=''):
	root = open('_WEB_/content/_navbar/navbar_content.html', 'r').read()

	navbar = root

	if active != "":
		rep = "{selected_"+active+"}"
		navbar = navbar.replace(rep, "active")
		try:
			addition = open('_WEB_/content/_navbar/navbar_content_{}.html'.format(active), 'r').read()
			navbar = navbar + addition
		except:
			pass


	return navbar

#this function is loaded into the BASE.moduls._Web_.Base.root as format_html()
# so its easy accessable from every request via self.format_html(html_string)
# it can call functions or just replace vars (can also ge given by **values)
def format_html_functions(self, html_string, **values):
	"""
	This function will take all
	|>>>func()<<<|
	in the .html,
	execute them and insert the return vaule as string.

	returns formated html
	"""

	search_results = re.finditer(self.format_html_regex ,html_string)
	for hit in search_results:
		try:
			calc_ = eval(hit.group(1))
			html_string = html_string.replace(hit.group(0), calc_)
		except:
			html_string = html_string.replace(hit.group(0), "")

	return html_string

def get_logged_in_btn(BASE, infos, platform=None, **replacements):
	if infos.get('user', None) == None:
		pls_login = open('_WEB_/content/_buttons/pls_login.html', 'r').read()
		return pls_login

	main_btn = open('_WEB_/content/_buttons/phaaze_loggedin.html', 'r').read()

	main_btn = main_btn.replace('{name}', infos.get('user', {}).get('phaaze_username', "[NAME N/A]"))
	main_btn = main_btn.replace('{type}', infos.get('user', {}).get('type', "[TYPE N/A]"))

	if infos.get('user', {}).get('img_path', None) != None:
		img = "HELLO"
	else:
		img = "hidden"
	main_btn = main_btn.replace('{img_path}', img)
	return main_btn
