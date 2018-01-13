#BASE.moduls._Web_.Base.root.admin

from importlib import reload
import traceback

def main(BASE, info, root):
	#/admin
	if len(info['path']) == 0:
		return admin(BASE, info)

	#leads to another site - /admin/[something]
	else:
		try:
			next_path = "root.admin.{0}.main".format(info['path'][0].lower())
			info['path'].pop(0)
			return eval(next_path+"(BASE, info, root)")

		except:
			return root.page_not_found.page_not_found(BASE, info, root)

def admin(BASE, info):
	return_header = [('Content-Type','text/html')]

	if info['cookies'].get('admin_session', None) != None:
		return admin_main(BASE, info)
	else:
		return admin_login(BASE, info)

def admin_main(BASE, info):
	return_header = [('Content-Type','text/html')]

	#get session
	search_str = 'data["session"] == "{}"'.format(info['cookies'].get('admin_session', None))
	res = BASE.PhaazeDB.select(of="session/admin", where=search_str)
	if len(res['data']) == 0:
		return admin_login(BASE, info, msg="Please login again. (Session expired)")

	#get admin user object
	admin_user = res["data"][0]

	site = open('_WEB_/content/admin/admin_main.html', 'r').read()
	res_user = BASE.PhaazeDB.select(of="admin/user", where='data["id"] == {}'.format(admin_user['user_id']))
	if len(res_user['data']) == 0:
		return admin_login(BASE, info, msg="Please login again. (User not found)")

	#get admin user object
	admin_user = res_user["data"][0]

	#Replace Parts
	site = site.replace("<!-- Navbar -->", BASE.moduls._Web_.Utils.get_navbar(active='admin'))
	site = site.replace("<!-- logged_in_user -->", format_loggedin_field(admin_user))

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
	r = r.replace("[name]", user.get("username", "--Name--"))
	r = r.replace("[type]", user.get("type", "N/A"))
	return r