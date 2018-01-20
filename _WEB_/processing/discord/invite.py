#BASE.moduls._Web_.Base.root.discord.invite

def invite(BASE, info, root, dump, msg="", server_id=""):
	return_header = [('Content-Type','text/html')]

	site = open("_WEB_\content\discord\discord_invite.html", 'r').read()

	site = site.replace("<!-- Navbar -->", BASE.moduls._Web_.Utils.get_navbar(active='discord'))
	try:
		if dump['discord_user_data'].get('avatar', "") != "":
			image_path = "avatars/{}/{}.png".format(dump['discord_user_data']['id'], dump['discord_user_data']['avatar'])
		else:
			image_path = "embed/avatars/{}.png".format(str( int(dump['discord_user_data']['discriminator']) % 5 ))

		site = site.replace("<!-- logged_in_user -->", BASE.moduls._Web_.Utils.discord_loggedin_field(image_path, dump['discord_user_data'].get('username', "-Username-")))
	except:
		pass
	site = site.replace("<!-- message -->", msg)

	if server_id != "":
		invite_link = "https://discordapp.com/oauth2/authorize?client_id=180679855422177280&scope=bot&permissions=8&guild_id="+server_id
	else:
		invite_link = "https://discordapp.com/oauth2/authorize?client_id=180679855422177280&scope=bot&permissions=8"

	site = site.replace("<!-- server_invite -->", invite_link)

	class r (object):
		content = site.encode("UTF-8")
		response = 200
		header = return_header
	return r










