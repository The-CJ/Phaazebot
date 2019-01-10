#BASE.modules._Web_.Base.root.wiki.wiki

import asyncio, json, html

# /wiki
async def main(self, request):
	# edit mode
	if request.query.get("edit", "") != "":
		return await edit(self, request)

	#search
	if request.query.get("search", None) != None:
		return await search(self, request)

	user_info = await self.root.get_user_info(request)
	current_navbar = self.root.html_header(self.root.BASE, active="wiki", user_info = user_info)

	wiki_site = request.match_info.get('site', "").lower()

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
	current_navbar = self.root.html_header(self.root.BASE, user_info = user_info, active="wiki")

	page_to_edit = request.query.get("edit", "").lower()
	if page_to_edit == "": return self.root.response(status=400)

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

# /wiki?search=.*
async def search (self, request):
	user_info = await self.root.get_user_info(request)
	current_navbar = self.root.html_header(self.root.BASE, user_info = user_info, active="wiki")

	search_query = request.query.get("search", "").lower()
	if search_query == "":
		w = "True"
	else:
		user_search = json.dumps(search_query)
		w = f"data['url_id'] == {user_search} or {user_search.lower()} in data['content'].lower() or {user_search.lower()} in data['tags']"

	page_search = self.root.BASE.PhaazeDB.select(
		of="wiki",
		where=w,
		fields=["url_id"]
	)

	page_hits = page_search.get("data", [])

	if not page_hits:
		query_results = f"<h2>No results found...</h2><h3>Create page: <a href=\"/wiki?edit={search_query}\">{search_query}</a></h3>"
	else:
		query_results = "".join(f"<h3 class=\"search-result\"><a href=\"/wiki/{html.escape(c['url_id'])}\">{html.escape(c['url_id'])}</a></h3>" for c in page_hits)

	wiki_edit_page = self.root.format_html(
		open('_WEB_/content/wiki/search.html', 'r', encoding='utf-8').read(),
		user_search=search_query,
		query_results=query_results
	)

	site = self.root.format_html(self.root.html_root,
		title="Phaaze | Wiki - Search",
		header=current_navbar,
		main=wiki_edit_page
	)

	return self.root.response(
		status=200,
		content_type='text/html',
		body=site
	)