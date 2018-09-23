#BASE.modules._Web_.Base.root.admin.admin

# /admin/manage-iser
async def main(self, request):
	user_info = await self.root.get_user_info(request)

	if user_info == None:
		return await self.login(request, msg="Login required")

	types = user_info.get("type", [])
	if not "admin" in [t.lower() for t in types]:
		return await self.action_not_allowed(request, msg="Admin rights reqired")

	site = self.root.html_root
	current_navbar = self.root.html_header(self.root.BASE, user_info = user_info, active="admin")
	main_site = open('_WEB_/content/admin/admin_manage-user.html','r').read()

	site = self.root.format_html(site,
		title="Phaaze | Admin - User manager",
		header=current_navbar,
		main=main_site
	)

	return self.root.response(
		body=site,
		status=200,
		content_type='text/html'
	)
