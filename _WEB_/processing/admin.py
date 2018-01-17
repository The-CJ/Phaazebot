#BASE.moduls._Web_.Base.root.admin

from importlib import reload
import traceback, html, os

def main(BASE, info, root):

	session = info['cookies'].get('admin_session', None)

	#no session -> login
	if session == None:
		return admin_login(BASE, info)

	#get session
	search_str = 'data["session"] == "{}"'.format(session)
	res = BASE.PhaazeDB.select(of="session/admin", where=search_str)
	if len(res['data']) == 0:
		#session not found -> login
		return admin_login(BASE, info, msg="Please login again. (Session expired)")

	#get session object
	admin_session = res["data"][0]

	#get admin user from session "user_id"
	search_str = 'data["id"] == {}'.format(admin_session['user_id'])
	res = BASE.PhaazeDB.select(of="admin/user", where=search_str)
	if len(res['data']) == 0:
		return admin_login(BASE, info, msg="Please login again. (User not found)")

	#get admin user object
	admin_user = res["data"][0]

	#store calculated data
	dump = dict()
	dump["session"] = admin_session
	dump["user"] = admin_user

	if len(info['path']) == 0:
		return admin_main(BASE, info, dump)

	elif info['path'][0] == "view-files":
		return view_page(BASE, info, dump)

	elif info['path'][0] == "edit-files":
		return edit_page(BASE, info, dump)

	else:
		return root.page_not_found.page_not_found(BASE, info, root)

def admin_main(BASE, info, dump):
	return_header = [('Content-Type','text/html')]

	site = open('_WEB_/content/admin/admin_main.html', 'r').read()

	#Replace Parts
	site = site.replace("<!-- Navbar -->", BASE.moduls._Web_.Utils.get_navbar(active='admin'))
	site = site.replace("<!-- logged_in_user -->", format_loggedin_field(dump['user']))

	#replace informations
	site = site.replace("{discord_active}", "checked" if BASE.active.discord else "")
	site = site.replace("{discord_bot_name}", BASE.phaaze.user.name)
	site = site.replace("{discord_bot_id}", BASE.phaaze.user.id)
	site = site.replace("{discord_bot_discriminator}", "#"+BASE.phaaze.user.discriminator)
	site = site.replace("{discord_bot_servers}", str(len(BASE.phaaze.servers)))
	site = site.replace("{discord_bot_avatar}", BASE.phaaze.user.avatar_url)

	site = site.replace("{twitch_active}", "checked" if BASE.active.twitch_irc else "")
	site = site.replace("{twitch_alert_active}", "checked" if BASE.active.twitch_alert else "")
	site = site.replace("{osu_active}", "checked" if BASE.active.osu_irc else "")
	site = site.replace("{web_active}", "checked" if BASE.active.web else "")

	class r (object):
		content = site.encode("UTF-8")
		response = 200
		header = return_header
	return r

def admin_login(BASE, info, msg=""):
	return_header = [('Content-Type','text/html')]
	site = open('_WEB_/content/admin/admin_login.html', 'r').read()

	site = site.replace("<!-- Navbar -->", BASE.moduls._Web_.Utils.get_navbar(active='admin'))

	class r (object):
		content = site.encode("UTF-8")
		response = 200
		header = return_header

	return r

def format_loggedin_field(user):
	r = """
          <div class="white">
            <span class="black-text align-middle inline" style="margin:0.5em;">([type]) - [name]</span>
            <button type="button" class="btn-danger align-middle inline expandable-btn waves-effect" style="padding:.3em;">
              <div class="material-icons align-middle inline">&nbsp;exit_to_app</div>
              <div class="align-middle inline expandable_content">
                <span onclick="javascript:admin_logout();">Logout</span>
              </div>
            </button>
          </div>
	"""
	r = r.replace("[name]", html.escape(user.get("username", "--Name--")))
	r = r.replace("[type]", user.get("type", "N/A"))
	return r

def view_page(BASE, info, dump):
	return_header = [('Content-Type','text/html')]

	site = open('_WEB_/content/admin/view.html', 'r').read()
	site = site.replace("<!-- Navbar -->", BASE.moduls._Web_.Utils.get_navbar(active='admin'))
	site = site.replace("<!-- logged_in_user -->", format_loggedin_field(dump['user']))

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

	class r (object):
		content = site.encode("UTF-8")
		response = 200
		header = return_header

	return r

def edit_page(BASE, info, dump):
	#TODO: much to do
	#https://highlightjs.org/download/

	return_header = [('Content-Type','text/html')]

	site = open('_WEB_/content/admin/edit.html', 'r').read()
	site = site.replace("<!-- Navbar -->", BASE.moduls._Web_.Utils.get_navbar(active='admin'))
	site = site.replace("<!-- logged_in_user -->", format_loggedin_field(dump['user']))

	page_index = info.get('values', {}).get("page", "main")
	try:
		content = open(page_index, 'r').read()
	except:
		content = "Can't open file: " + page_index

	site = site.replace("<!-- page_content -->", html.escape(content))
	site = site.replace("<!-- page_index -->", html.escape(page_index))

	class r (object):
		content = site.encode("UTF-8")
		response = 200
		header = return_header
	return r
