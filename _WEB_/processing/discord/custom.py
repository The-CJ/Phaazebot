#BASE.moduls._Web_.Base.root.discord.custom

def custom(BASE, info, root, dump, msg=""):
	return_header = [('Content-Type','text/html')]

	site = open("_WEB_\content\discord\discord_custom_view.html", 'r').read()
	site = site.replace("<!-- Navbar -->", BASE.moduls._Web_.Utils.get_navbar(active='discord'))
	site = site.replace("<!-- message -->", msg)

	server_id = info.get("path", [None])[0]
	if server_id == None:
		return BASE.moduls._Web_.Base.root.discord.invite.invite(BASE, info, root, dump, msg="Seems Like Phaaze is not on this server.", server_id=server_id)

	server_file = BASE.call_from_async( BASE.moduls.Utils.get_server_file(BASE, server_id, prevent_new=True), BASE.Discord_loop )

	if server_file == None:
		return BASE.moduls._Web_.Base.root.discord.invite.invite(BASE, info, root, dump, msg="Seems Like Phaaze is not on this server.", server_id=server_id)

	site = site.replace("<!-- server_id -->", server_id)

	class r (object):
		content = site.encode("UTF-8")
		response = 200
		header = return_header
	return r










