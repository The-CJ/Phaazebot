#BASE.moduls._Web_.Base.root.discord.main

import http.cookies as cookie
from importlib import reload
import asyncio

def main(BASE, info, dirs):
	#/discord
	if len(info['path']) == 0:
		return discord(BASE, info)

	#leads to another site - /discord/[something]
	else:
		try:
			next_file = "dirs.discord.{0}.main.main".format(info['path'][0].lower())
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
	nav = open('_WEB_/content/navbar_content.html', 'r').read()

	site = site.replace("<!-- Navbar -->", nav)

	class r (object):
		content = site.encode("UTF-8")
		response = 200
		header = return_header
	return r

def discord_login(BASE, info):
	return_header = [('Content-Type','text/html')]
	site = open('_WEB_/content/discord/discord_login.html', 'r').read()
	nav = open('_WEB_/content/navbar_content.html', 'r').read()

	site = site.replace("<!-- Navbar -->", nav)
	future = asyncio.run_coroutine_threadsafe(BASE.phaaze.application_info(), BASE.Discord_loop)
	result = future.result()

	site = site.replace("__Discord_Client_ID__", result.id)

	class r (object):
		content = site.encode("UTF-8")
		response = 200
		header = return_header

	return r

async def get_discord_bot_infos(BASE, f):
	x = await BASE.phaaze.application_info()
	f.set_result('werwr')
