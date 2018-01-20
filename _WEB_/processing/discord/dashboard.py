#BASE.moduls._Web_.Base.root.discord.dashboard

import http.cookies as cookie
from importlib import reload
import asyncio, datetime, requests, html, time

DISCORD_BOT_ID = "180679855422177280"

def main(BASE, info, root, dump):
	#/discord/dashboard
	if len(info['path']) == 0:
		server_id = None
	else:
		server_id = info['path'][0]

	return dashboard(BASE, info, root, dump, server_id)


def dashboard(BASE, info, root, dump, server_id):
	return_header = [('Content-Type','text/html')]
	site = open('_WEB_/content/discord/discord_dashboard.html', 'r').read()

	#load avatar
	if dump['discord_user_data'].get('avatar', "") != "":
		image_path = "avatars/{}/{}.png".format(dump['discord_user_data']['id'], dump['discord_user_data']['avatar'])
	else:
		image_path = "embed/avatars/{}.png".format(str( int(dump['discord_user_data']['discriminator']) % 5 ))

	#get server object
	discord_server_data = BASE.api.discord.get_server(BASE, server_id=server_id)
	if discord_server_data.get("code", None) == 50001:
		return BASE.moduls._Web_.Base.root.discord.invite.invite(BASE, info, root, dump, msg="Seems Like Phaaze is not on this server.", server_id=server_id)

	saved_settings = BASE.call_from_async( BASE.moduls.Utils.get_server_file(BASE, server_id), BASE.Discord_loop )

	#Finish up -- Replace Parts
	site = site.replace("<!-- Navbar -->", BASE.moduls._Web_.Utils.get_navbar(active='discord'))
	site = site.replace("<!-- logged_in_user -->", BASE.moduls._Web_.Utils.discord_loggedin_field(image_path, dump['discord_user_data'].get('username', "-Username-")))
	site = site.replace("<!-- Server_name -->", html.escape(discord_server_data.get('name', "[Server N/A]")))
	site = site.replace("<!-- json_return__data -->", html.escape(str(discord_server_data)))
	site = site.replace("<!-- json_return__data_info -->", html.escape(str(saved_settings)))

	#add profile Picture

	class r (object):
		content = site.encode("UTF-8")
		response = 200
		header = return_header
	return r
