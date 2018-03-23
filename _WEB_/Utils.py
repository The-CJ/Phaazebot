#BASE.moduls._Web_.Utils

import html, re

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

def format_html_functions(BASE, html_string, infos = {}):
	"""
	This function will take all
	|>>>func()<<<|
	in the .html,
	execute them and insert the return vaule as string.

	returns formated html
	"""

	search_results = re.finditer(r"\|>>>(.+)<<<\|" ,html_string)
	for hit in search_results:
		try:
			calc_ = eval(hit.group(1))
			html_string = html_string.replace(hit.group(0), calc_)
		except:
			continue

	return html_string

def get_logged_in_btn(BASE, temp=None, **replacements):
	if temp == None:
		temp = """
          <button type="button" name="button">|Example|</button>
		"""
	for thing in replacements:
		temp = temp.replace('{'+thing+'}', replacements[thing])

	return temp