#BASE.moduls._Web_.Base.root.discord.login.main

import http.cookies as cookie
from importlib import reload
import asyncio, datetime, requests

def main(BASE, info, dirs):
	#/discord/login
	if len(info['path']) == 0:
		return login(BASE, info)

	#leads to another site - /discord/login/[something]
	else:
		try:
			next_file = "dirs.discord.login.{0}.main".format(info['path'][0].lower())
			info['path'].pop(0)
			return eval(next_path+"(BASE, info, dirs)")

		except:
			return dirs.page_not_found.page_not_found(BASE, info, dirs)

def login(BASE, info):
	code = info["values"].get("code")

	if code == None:
		return_header = [("Location", "/discord?error")]
		class r (object):
			content = "".encode("UTF-8")
			response = 301
			header = return_header
		return r

	data = {'client_id': BASE.access.Discord_Phaaze_id,
			'client_secret': BASE.access.Discord_Phaaze_secret,
			'grant_type': 'authorization_code',
			'code': code,
			'redirect_uri': "http://phaaze.net/discord/login"}

	headers = {'Content-Type': 'application/x-www-form-urlencoded'}

	r = requests.post('https://discordapp.com/api/v6/oauth2/token', data, headers)
	r.raise_for_status()
	r=r.json()

	save_object = dict(
		session = BASE.moduls._Web_.Base.Utils.get_session_key(),
		access_token = r.get('access_token', None),
		token_type = r.get('token_type', None),
		refresh_token = r.get('refresh_token', None),
		scope = r.get('scope', None)
	)

	BASE.PhaazeDB.insert(into="session/discord", content=save_object)

	class r (object):
		return_header = [('Set-Cookie','discord_session='+save_object['session']), ("Location", "/discord")]

		content = b""
		response = 302
		header = return_header
	return r
