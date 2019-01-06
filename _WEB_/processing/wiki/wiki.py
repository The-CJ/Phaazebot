#BASE.modules._Web_.Base.root.wiki.wiki

import asyncio, json

# /wiki
async def main(self, request):
	# edit mode
	if request.query.get("edit", "") != "":
		return await edit(self, request)

	user_info = await self.root.get_user_info(request)
	current_navbar = self.root.html_header(self.root.BASE, user_info = user_info)

	wiki_site = request.match_info.get('site', None)

	# no site define -> show main
	if wiki_site == None or wiki_site == "":
		main_wiki = open('_WEB_/content/wiki/main.html', 'r', encoding='utf-8').read()
		site = self.root.format_html(self.root.html_root,
			title="Phaaze | Wiki",
			header=current_navbar,
			main=main_wiki
		)

		return self.root.response(
			status=200,
			content_type='text/html',
			body=site
		)

	# get page
	page_res = self.root.BASE.PhaazeDB.select(of="wiki", where=f"data['url_id'] == {json.dumps(wiki_site)}")
	page_res_hits = page_res.get("hits", 0)

	# not found, (ask for create)
	if page_res_hits == 0:
		pnf = open('_WEB_/content/wiki/not_found.html', 'r', encoding='utf-8').read()
		pnf_site = self.root.format_html(self.root.html_root,
			title="Phaaze | Wiki - Not Found",
			header=current_navbar,
			main=self.root.format_html(pnf, url_id=wiki_site)
		)

		return self.root.response(
			status=200,
			content_type='text/html',
			body=pnf_site
		)

	found_page = page_res.get("data", [None])[0]

	# should never happen, but hey
	if found_page == None:
		return await self.root.web.page_not_found(msg="Getting wiki info returned nothing... that should not happen")

	wiki_site = self.root.format_html(self.root.html_root,
		title="Phaaze | Wiki - "+found_page.get("url_id", "???"),
		header=current_navbar,
		main=found_page.get("content", "Error returning content")
	)

	return self.root.response(
		status=200,
		content_type='text/html',
		body=wiki_site
	)

# /wiki?edit=.*
async def edit(self, request):
	user_info = await self.root.get_user_info(request)
	current_navbar = self.root.html_header(self.root.BASE, user_info = user_info)

	page_to_edit = request.query.get("edit", None)
	if page_to_edit == None: self.root.response(status=400)

	# not allowed to edit
	if not self.root.check_role(user_info, ['superadmin', 'admin', 'wiki moderator']):
		return await self.root.web.action_not_allowed(request, msg="You don't have permissions to edit the wiki")

	j = dict(of="user", limit=1, where="int(user['id']) == int(data['edited_by'])", store="user")
	page_res = self.root.BASE.PhaazeDB.select(of="wiki", where=f"data['url_id'] == {json.dumps(page_to_edit)}", join=j)

	# gather user infos
	if page_res.get("data", []):
		page_to_edit_entry = page_res["data"][0]
		edited_at = page_to_edit_entry.get("edited_at", "[N/A]")
		edit_tags = ",".join(page_to_edit_entry.get("tags", []))
		user = page_to_edit_entry.get("user", [])

		if len(user) == 0:
			edited_by_name = "Unknown"
			edited_by_id = "Unknown"
		else:
			edited_by_name = user[0].get("username", "Unknown")
			edited_by_id = user[0].get("id", "Unknown")
	else:
		page_to_edit_entry = None
		edited_at = "Never"
		edited_by_name = "None"
		edited_by_id = "0"
		edit_tags=""

	wiki_edit_page = self.root.format_html(
		open('_WEB_/content/wiki/edit.html', 'r', encoding='utf-8').read(),
		action="Edit" if page_to_edit_entry != None else "Create",
		url_id=page_to_edit,
		last_user_name=edited_by_name,
		last_user_id=edited_by_id,
		last_date=edited_at,
		tags=edit_tags,
		content=page_to_edit_entry.get("content", "[N/A]") if page_to_edit_entry != None else "",
	)

	site = self.root.format_html(self.root.html_root,
		title="Phaaze | Wiki - Edit: "+page_to_edit,
		header=current_navbar,
		main=wiki_edit_page
	)

	return self.root.response(
		status=200,
		content_type='text/html',
		body=site
	)

