#BASE.moduls._Web_.Base.root.discord.main

import http.cookies as cookie
from importlib import reload
import asyncio, datetime, requests, html

DISCORD_BOT_ID = "180679855422177280"

def main(BASE, info, root):
	#/discord/dashboard
	if len(info['path']) == 0:
		server_id = None
	else:
		server_id = info['path'][0]

	return dashboard(BASE, info, server_id)


def dashboard(BASE, info, server_id):
	return_header = [('Content-Type','text/html')]
	site = open('_WEB_/content/discord/discord_dashboard.html', 'r').read()

	#get session
	search_str = 'data["session"] == "{}"'.format(info['cookies'].get('discord_session', None))
	res = BASE.PhaazeDB.select(of="session/discord", where=search_str)
	if len(res['data']) == 0:
		return BASE.moduls._Web_.Base.root.discord.main.discord_login(BASE, info, msg="Please login again. (Session expired)")

	#get discord user object from db
	user_db_data = res["data"][0]
	discord_user_data = BASE.api.discord.get_user(BASE, oauth_key=user_db_data.get("access_token", ""))
	if discord_user_data.get('id', None) == None:
		return BASE.moduls._Web_.Base.root.discord.main.discord_login(BASE, info, msg="Please login again.<br>(401 Discord Unauthorized)")

	#load avatar
	if discord_user_data.get('avatar', "") != "":
		image_path = "avatars/{}/{}.png".format(discord_user_data['id'], discord_user_data['avatar'])
	else:
		image_path = "embed/avatars/{}.png".format(str( int(discord_user_data['discriminator']) % 5 ))

	#get server object
	discord_server_data = BASE.api.discord.get_server(BASE, server_id=server_id)
	if discord_server_data.get("code", None) == 50001:
		# TODO: Message to User that Phaaze is not on this server and invite
		print("Can't show")

	#get saved settings
	#file_call = BASE.moduls.Utils.get_server_file(BASE, server_id)
	#loop = asyncio.new_event_loop()
	#file = loop.run_until_complete(file_call)
	#print(file)
	#FIXME: #Get Files Somehow..... pls send help



	#Finish up -- Replace Parts
	site = site.replace("<!-- Navbar -->", BASE.moduls._Web_.Utils.get_navbar(active='discord'))
	site = site.replace("<!-- logged_in_user -->", BASE.moduls._Web_.Utils.discord_loggedin_field(image_path, discord_user_data.get('username', "-Username-")))
	site = site.replace("<!-- Server_name -->", discord_server_data.get('name', "[Server N/A]"))
	site = site.replace("<!-- json_return__data -->", html.escape(str(discord_server_data)))

	#add profile Picture

	class r (object):
		content = site.encode("UTF-8")
		response = 200
		header = return_header
	return r
