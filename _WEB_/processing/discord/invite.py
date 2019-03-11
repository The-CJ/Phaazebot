import asyncio

# /discord/invite
async def main(self, request):
	user_info = await self.root.get_user_info(request)

	main_site = open("_WEB_\content\discord\discord_invite.html", 'r').read()
	current_navbar = self.root.html_header(self.root.BASE, user_info = user_info, active="admin")

	site = site.replace("<!-- server_invite -->", invite_link)

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









