#BASE.moduls._Web_.Base.root.discord.main

import http.cookies as cookie
from importlib import reload
import asyncio, datetime, requests

DISCORD_BOT_ID = "180679855422177280"

def main(BASE, info, dirs):
	#/discord
	if len(info['path']) == 0:
		return discord(BASE, info)

	#leads to another site - /discord/[something]
	else:
		try:
			next_path = "dirs.discord.{0}.main".format(info['path'][0].lower())
			info['path'].pop(0)
			return eval(next_path+"(BASE, info, dirs)")

		except:
			return dirs.page_not_found.page_not_found(BASE, info, dirs)

def discord(BASE, info):
	return_header = [('Content-Type','text/html')]

	if info['cookies'].get('discord_session', None) != None:
		return discord_main(BASE, info)
	else:
		return discord_login(BASE, info)

def discord_main(BASE, info):
	return_header = [('Content-Type','text/html')]
	site = open('_WEB_/content/discord/discord_main.html', 'r').read()

	#get session
	search_str = 'data["session"] == "{}"'.format(info['cookies'].get('discord_session', None))
	res = BASE.PhaazeDB.select(of="session/discord", where=search_str)
	if len(res['data']) == 0:
		return discord_login(BASE, info, msg="Please login again. (Session expired)")

	#get discord user object
	user_db_data = res["data"][0]
	discord_user_data = BASE.api.discord.get_user(BASE, oauth_key=user_db_data.get("access_token", ""))
	if discord_user_data.get('id', None) == None:
		return discord_login(BASE, info, msg="Please login again.<br>(401 Discord Unauthorized)")

	#load avatar
	if discord_user_data.get('avatar', "") != "":
		image_path = "avatars/{}/{}.png".format(discord_user_data['id'], discord_user_data['avatar'])
	else:
		image_path = "embed/avatars/{}.png".format(str( int(discord_user_data['discriminator']) % 5 ))

	#Replace Parts
	site = site.replace("<!-- Navbar -->", BASE.moduls._Web_.Utils.get_navbar(active='discord'))
	site = site.replace("<!-- logged_in_user -->", format_loggedin_field(image_path, discord_user_data.get('username', "-Username-")))


	#add profile Picture

	class r (object):
		content = site.encode("UTF-8")
		response = 200
		header = return_header
	return r

def discord_login(BASE, info, msg=""):
	return_header = [('Content-Type','text/html')]
	site = open('_WEB_/content/discord/discord_login.html', 'r').read()

	site = site.replace("<!-- Navbar -->", BASE.moduls._Web_.Utils.get_navbar(active='discord'))

	site = site.replace("__Discord_Client_ID__", DISCORD_BOT_ID)
	site = site.replace("__Nonce_of_stuff__", str(datetime.datetime.timestamp(datetime.datetime.now())))

	if info['values'].get('error', False) and msg=="":
		site = site.replace("<!-- Error -->", "Login failed, pls try later again...")

	elif msg != "":
		site = site.replace("<!-- Error -->", msg)

	class r (object):
		content = site.encode("UTF-8")
		response = 200
		header = return_header

	return r

def format_loggedin_field(image_path, name):
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
	r = r.replace("[name]", name)
	r = r.replace("[path]", image_path)
	return r