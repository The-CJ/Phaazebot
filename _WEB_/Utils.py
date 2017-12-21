#BASE.moduls._Web_.Utils



def get_navbar(active=''):
	root = open('_WEB_/content/_navbar/navbar_content.html', 'r').read()

	navbar = root

	if active != "":
		rep = "{selected_"+active+"}"
		navbar = navbar.replace(rep, "selected_option")

	return navbar

