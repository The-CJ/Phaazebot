#BASE.modules._Web_.Base.root.discord.dashboard

import http.cookies as cookie
from importlib import reload
import asyncio, datetime, requests, html, time, discord

def main(BASE, info, root, dump):
	#/discord/dashboard
	if len(info['path']) == 0:
		server_id = None
	else:
		server_id = info['path'][0]

	return dashboard(BASE, info, root, dump, server_id)

def dashboard(BASE, info, root, dump, server_id):
	discord_server = BASE.discord.get_server(server_id)
	if discord_server == None:
		return BASE.modules._Web_.Base.root.discord.invite.invite(BASE, info, root, dump, msg="Seems Like Phaaze is not on this server.", server_id=server_id)

	discord_member = discord_server.get_member(dump['discord_user_data'].get('id', None))
	if discord_member == None:
		return root.action_not_allowed.action_not_allowed(BASE, info, root)

	perm = discord_member.server_permissions
	if not (perm.manage_server or perm.administrator):
		return root.action_not_allowed.action_not_allowed(BASE, info, root)

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
		return BASE.modules._Web_.Base.root.discord.invite.invite(BASE, info, root, dump, msg="Seems Like Phaaze is not on this server.", server_id=server_id)

	saved_settings = BASE.call_from_async( BASE.modules.Utils.get_server_file(BASE, server_id, prevent_new=True), BASE.Discord_loop )
	server_object = BASE.discord.get_server(server_id)

	#Finish up -- Replace Parts
	site = site.replace("<!-- Server_name -->", html.escape(discord_server_data.get('name', "[Server N/A]")))
	site = site.replace("<!-- saved_settings.id -->", server_object.id)

	site = site.replace("<!-- len(saved_settings['commands']) -->", str(len(saved_settings.get('commands', []))))

	info['root'] = root
	info['dump'] = dump
	info['server_id'] = server_id
	site = BASE.modules._Web_.Utils.format_html_functions(BASE, site, infos = info)

	#add profile Picture

	class r (object):
		content = site.encode("UTF-8")
		response = 200
		header = return_header
	return r
