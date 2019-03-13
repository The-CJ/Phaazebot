import asyncio

# /admin/manage-user
async def main(self, request):
	user_info = await self.root.get_user_info(request)

	if user_info == None:
		return await self.login(request, msg="Login required")

	if not self.root.check_role(user_info, ['admin', 'image uploader']):
		return await self.action_not_allowed(request, msg="Admin rights reqired")

	site = self.root.html_root
	current_navbar = self.root.html_header(self.root.BASE, user_info = user_info, active="admin")
	main_site = open('_WEB_/content/admin/admin_manage-image.html','r').read()

	site = self.root.format_html(site,
		title="Phaaze | Admin - Image manager",
		header=current_navbar,
		main=main_site
	)

	return self.root.response(
		body=site,
		status=200,
		content_type='text/html'
	)

