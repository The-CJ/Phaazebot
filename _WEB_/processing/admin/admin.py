#BASE.modules._Web_.Base.root.admin.admin

import html, os

# /admin
async def main(self, request):

	site = self.root.html_root
	user_info = await self.root.get_user_info(request)

	if user_info == None:
		return await self.login(request, msg="Login required")

	types = user_info.get("type", [])
	if not "admin" in [t.lower() for t in types]:
		return await self.action_not_allowed(request, msg="Admin rights reqired")

	current_navbar = self.root.html_header(self.root.BASE, user_info = user_info, active="admin")
	main_site = open('_WEB_/content/admin/admin_main.html','r').read()

	site = self.root.format_html(site,
		title="Phaaze | Admin",
		header=current_navbar,
		main=main_site
	)

	return self.root.response(
		body=site,
		status=200,
		content_type='text/html'
	)

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
		return BASE.modules._Web_.Base.root.page_not_found.page_not_found(BASE, info, None)

	folder_spec = dict()

	path_str = path + "/" if path != "" else ""
	for file_or_folder in folder:
		if os.path.isfile(path_str+file_or_folder):
			folder_spec[file_or_folder] = 'file'

		else:
			folder_spec[file_or_folder] = 'folder'

	site = site.replace("{'name':'type'}", str(folder_spec))
	site = site.replace("[js_var_path]", str("'"+js_var_path+"'"))

	site = BASE.modules._Web_.Utils.format_html_functions(BASE, site, infos = info)
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

	site = BASE.modules._Web_.Utils.format_html_functions(BASE, site, infos = info)
	class r (object):
		content = site.encode("UTF-8")
		response = 200
		header = return_header
	return r
