#BASE.modules._Web_.Base.root.discord.main

import http.cookies as cookie
from importlib import reload
import asyncio, datetime, requests, html

DISCORD_BOT_ID = "180679855422177280"

def main(BASE, info, root):
	dump = dict()
	#accessable without login
	if len(info['path']) > 0:
		#/invite
		if info['path'][0].lower() == "invite":
			info['path'].pop(0)
			return root.discord.invite.invite(BASE, info, root, dump)

		#/custom
		if info['path'][0].lower() == "custom":
			info['path'].pop(0)
			return root.discord.custom.custom(BASE, info, root, dump)

	if info['cookies'].get('discord_session', None) == None:
		return discord_login(BASE, info)

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

	dump['discord_user_data'] = discord_user_data

	####################################################

	#/discord
	if len(info['path']) == 0:
		return discord_main(BASE, info, dump)

	#/dashboard
	elif info['path'][0].lower() == "dashboard":
		info['path'].pop(0)
		return root.discord.dashboard.main(BASE, info, root, dump)

	#/invite
	elif info['path'][0].lower() == "invite":
		info['path'].pop(0)
		return root.discord.invite.invite(BASE, info, root, dump)

	else:
		return root.page_not_found.page_not_found(BASE, info, root)

def discord_main(BASE, info, dump):
	return_header = [('Content-Type','text/html')]
	site = open('_WEB_/content/discord/discord_main.html', 'r').read()

	#load avatar
	if dump['discord_user_data'].get('avatar', "") != "":
		dump['image_path'] = "avatars/{}/{}.png".format(dump['discord_user_data']['id'], dump['discord_user_data']['avatar'])
	else:
		dump['image_path'] = "embed/avatars/{}.png".format(str( int(dump['discord_user_data']['discriminator']) % 5 ))

	#Replace Parts
	site = site.replace("<!-- Navbar -->", BASE.modules._Web_.Utils.get_navbar(active='discord'))

	info['dump'] = dump
	site = BASE.modules._Web_.Utils.format_html_functions(BASE, site, infos = info)

	#add profile Picture

	class r (object):
		content = site.encode("UTF-8")
		response = 200
		header = return_header
	return r

def discord_login(BASE, info, msg=""):
	return_header = [('Content-Type','text/html')]
	site = open('_WEB_/content/discord/discord_login.html', 'r').read()

	site = site.replace("__Discord_Client_ID__", DISCORD_BOT_ID)
	site = site.replace("__Nonce_of_stuff__", str(datetime.datetime.timestamp(datetime.datetime.now())))

	if info['values'].get('error', False) and msg=="":
		site = site.replace("<!-- Error -->", "Login failed, pls try later again...")

	elif msg != "":
		site = site.replace("<!-- Error -->", msg)

	site = BASE.modules._Web_.Utils.format_html_functions(BASE, site, infos = info)

	class r (object):
		content = site.encode("UTF-8")
		response = 200
		header = return_header

	return r
