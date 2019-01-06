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
		main_wiki = open('_WEB_/content/wiki/root.html', 'r', encoding='utf-8').read()
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

async def edit(self, request):
	user_info = await self.root.get_user_info(request)
	current_navbar = self.root.html_header(self.root.BASE, user_info = user_info)

	page_to_edit = request.query.get("edit", None)
	if page_to_edit == None: self.root.response(status=400)

	site = self.root.format_html(self.root.html_root,
		title="Phaaze | Wiki - Edit: "+page_to_edit,
		header=current_navbar,
		main="HIER"
	)

	return self.root.response(
		status=200,
		content_type='text/html',
		body=site
	)

def wiki(BASE, info):
	return_header = [('Content-Type','text/html')]

	site = open('_WEB_/content/wiki/root.html', 'r', encoding='utf-8').read()

	page_index = info.get('values', {}).get("page", "main")
	page_index = page_index.replace('..', '')
	if page_index.startswith('/'):
		page_index = " N/A"

	try:
		content = open('_WEB_/content/wiki/pages/{}.html'.format(page_index), 'r', encoding='utf-8').read()
	except:
		content = open('_WEB_/content/wiki/not_found.html', 'r', encoding='utf-8').read()
		content = content.replace("<!-- tryed_path -->", page_index)

	site = site.replace("<!-- about_content -->", content)
	site = BASE.modules._Web_.Utils.format_html_functions(BASE, site, infos = info)
	class r (object):
		content = site.encode("UTF-8")
		response = 200
		header = return_header
	return r

