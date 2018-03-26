#BASE.moduls._Web_.Base.root.admin.admin

import  html, os

def main(BASE, info, root):

	#no session -> login
	if info.get('user', None) == None:
		return admin_login(BASE, info)

	if "admin" not in info.get('user', {}).get("type", "").lower():
		return admin_login(BASE, info, msg="Your Account is unauthoriesed to access.")

	if len(info['path']) == 0:
		return admin_main(BASE, info)

	elif info['path'][0] == "view-files":
		return view_page(BASE, info)

	elif info['path'][0] == "edit-files":
		return edit_page(BASE, info)

	else:
		return root.page_not_found.page_not_found(BASE, info, root)

def admin_main(BASE, info, msg=""):
	return_header = [('Content-Type','text/html')]

	site = open('_WEB_/content/admin/admin_main.html', 'r').read()

	#Replace Parts
	site = site.replace("<!-- msg -->", msg)

	site = BASE.moduls._Web_.Utils.format_html_functions(BASE, site, infos = info)

	class r (object):
		content = site.encode("UTF-8")
		response = 200
		header = return_header
	return r

def admin_login(BASE, info, msg=""):
	return_header = [('Content-Type','text/html')]
	site = open('_WEB_/content/admin/admin_login.html', 'r').read()
	site = site.replace("<!-- msg -->", msg)

	site = BASE.moduls._Web_.Utils.format_html_functions(BASE, site, infos = info)

	class r (object):
		content = site.encode("UTF-8")
		response = 200
		header = return_header

	return r

def view_page(BASE, info):
	return_header = [('Content-Type','text/html')]

	site = open('_WEB_/content/admin/view.html', 'r').read()

	path = info['values'].get('path', "")
	js_var_path = ""

	try:
		if path == "":
			folder = os.listdir()
		else:
			js_var_path += path + "/"
			folder = os.listdir(path)
	except:
		return BASE.moduls._Web_.Base.root.page_not_found.page_not_found(BASE, info, None)

	folder_spec = dict()

	path_str = path + "/" if path != "" else ""
	for file_or_folder in folder:
		if os.path.isfile(path_str+file_or_folder):
			folder_spec[file_or_folder] = 'file'

		else:
			folder_spec[file_or_folder] = 'folder'

	site = site.replace("{'name':'type'}", str(folder_spec))
	site = site.replace("[js_var_path]", str("'"+js_var_path+"'"))

	site = BASE.moduls._Web_.Utils.format_html_functions(BASE, site, infos = info)
	class r (object):
		content = site.encode("UTF-8")
		response = 200
		header = return_header

	return r

def edit_page(BASE, info):
	return_header = [('Content-Type','text/html')]

	site = open('_WEB_/content/admin/edit.html', 'r').read()

	page_index = info.get('values', {}).get("page", "main")
	try:
		content = open(page_index, 'r').read()
	except:
		content = "Can't open file: " + page_index

	site = site.replace("<!-- page_content -->", html.escape(content))
	site = site.replace("<!-- page_index -->", html.escape(page_index))

	site = BASE.moduls._Web_.Utils.format_html_functions(BASE, site, infos = info)
	class r (object):
		content = site.encode("UTF-8")
		response = 200
		header = return_header
	return r
