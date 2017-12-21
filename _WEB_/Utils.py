#BASE.moduls._Web_.Utils



def get_navbar(active=''):
	root = open('_WEB_/content/_navbar/navbar_content.html', 'r').read()

	navbar = root

	if active != "":
		rep = "{selected_"+active+"}"
		navbar = navbar.replace(rep, "selected_option")
		try:
			addition = open('_WEB_/content/_navbar/navbar_content_{}.html'.format(active), 'r').read()
			navbar = navbar + addition
		except:
			pass


	return navbar

