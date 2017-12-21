#BASE.moduls._Web_.Utils



def get_navbar(active=''):
	root = open('_WEB_/content/_navbar/navbar_content.html', 'r').read()
	
	dis_nav = open('_WEB_/content/_navbar/navbar_discord_content.html', 'r').read()
	db_nav = open('_WEB_/content/_navbar/navbar_db_content.html', 'r').read()
	twitch_nav = open('_WEB_/content/_navbar/navbar_twitch_content.html', 'r').read()
	osu_nav = open('_WEB_/content/_navbar/navbar_osu_content.html', 'r').read()
	twitter_nav = open('_WEB_/content/_navbar/navbar_twitter_content.html', 'r').read()

	navbar = root
	navbar = navbar.replace("<!-- DiscordNavbar -->", dis_nav)
	navbar = navbar.replace("<!-- DBNavbar -->", db_nav)
	navbar = navbar.replace("<!-- TwitchNavbar -->", twitch_nav)
	navbar = navbar.replace("<!-- OsuNavbar -->", osu_nav)
	navbar = navbar.replace("<!-- TwitterNavbar -->", twitter_nav)

	if active != "":
		rep = "{is_on_"+active+"}"
		navbar = navbar.replace(rep, "show")

	return navbar

