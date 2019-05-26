from Utils.Classes.htmlformatter import HTMLFormatter

def getNavbar(active:str="", user_info=None) -> HTMLFormatter:
	Navbar:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Navbar/default.html")

	Navbar.replace(login_button=getLoginButton(user_info=user_info))

	Navbar.setRegex(r"\{selected_(.+?)\}")
	Navbar.replace(replace_empty=True, **{active:"active"})

	return Navbar

def getLoginButton(user_info=None) -> HTMLFormatter:
	Button:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Button/account.html")
	field_replace:str = "loggedin" if user_info else ""
	Button.replace(is_logged_in=field_replace)

	return Button
