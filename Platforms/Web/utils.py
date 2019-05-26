from Utils.Classes.htmlformatter import HTMLFormatter

def getNavbar(active:str="", user_info=None) -> HTMLFormatter:
	navbar:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Navbar/default.html")



	navbar.setRegex(r"\{selected_(.+?)\}")
	navbar.replace(replace_empty=True, **{active:"active"})

	return navbar

def getButton() -> HTMLFormatter:
	pass
