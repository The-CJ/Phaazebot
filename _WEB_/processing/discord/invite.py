#BASE.moduls._Web_.Base.root.discord.invite

def invite(BASE, info, root, dump, msg="", server_id=""):
	return_header = [('Content-Type','text/html')]

	site = open("_WEB_\content\discord\discord_invite.html", 'r').read()

	site = site.replace("<!-- Navbar -->", BASE.moduls._Web_.Utils.get_navbar(active='discord'))

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










