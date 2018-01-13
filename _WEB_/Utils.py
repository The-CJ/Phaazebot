#BASE.moduls._Web_.Utils

import html

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

def discord_loggedin_field(image_path, name):
	r = """
          <div class="white" style="border-radius:25px;">
            <img style="height:2em;margin:0.5em;" class="profil_picture inline align-middle" src="https://cdn.discordapp.com/[path]" alt="Avatar">
            <span class="black-text align-middle inline" style="margin-right:0.5em">[name]</span>
            <button type="button" class="btn-danger align-middle inline expandable-btn waves-effect" style="border-radius:25px;padding:.7em;">
              <div class="material-icons align-middle inline">&nbsp;exit_to_app</div>
              <div class="align-middle inline expandable_content">
                <span onclick="javascript:discord_logout();">Logout</span>
              </div>
            </button>
          </div>
	"""
	r = r.replace("[name]", html.escape(name))
	r = r.replace("[path]", image_path)
	return r