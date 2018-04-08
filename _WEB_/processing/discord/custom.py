#BASE.moduls._Web_.Base.root.discord.custom

import html

def custom(BASE, info, root, dump, msg=""):
	return_header = [('Content-Type','text/html')]

	site = open("_WEB_\content\discord\discord_custom_view.html", 'r').read()
	site = site.replace("<!-- message -->", msg)

	server_id = info.get("path", [None])[0]
	if server_id == None:
		return BASE.moduls._Web_.Base.root.discord.invite.invite(BASE, info, root, dump, msg="Seems Like Phaaze is not on this server.", server_id=server_id)

	server = BASE.phaaze.get_server(server_id)

	if server == None:
		return BASE.moduls._Web_.Base.root.discord.invite.invite(BASE, info, root, dump, msg="Seems Like Phaaze is not on this server.", server_id=server_id)

	site = site.replace("<!-- server_id -->", server_id)
	site = site.replace("<!-- server.name -->", html.escape(server.name))

	site = BASE.moduls._Web_.Utils.format_html_functions(BASE, site, infos = info)
	class r (object):
		content = site.encode("UTF-8")
		response = 200
		header = return_header
	return r










