import asyncio

DISCORD_BOT_CLIENT_ID = "180679855422177280"

# /discord/invite
async def main(self, request, msg="", server_id=None):
	user_info = await self.root.get_user_info(request)

	main_site = open("_WEB_/content/discord/discord_invite.html", 'r').read()
	current_navbar = self.root.html_header(self.root.BASE, user_info = user_info, active="discord")

	invite_link = f"https://discordapp.com/oauth2/authorize?client_id={DISCORD_BOT_CLIENT_ID}&scope=bot&permissions=8"

	check_id = server_id or request.query.get("server_id", None)
	if check_id != None:
		invite_link += f"&guild_id={check_id}"

	main_site = self.root.format_html(main_site,
		message=msg,
		invite_link=invite_link
	)

	site = self.root.format_html(self.root.html_root,
		title="Phaaze | Discord - Invite",
		header=current_navbar,
		main=main_site
	)

	return self.root.response(
		body=site,
		status=200,
		content_type='text/html'
	)









