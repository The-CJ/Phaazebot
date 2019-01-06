#BASE.modules._Web_.Base.root.wiki.wiki

import asyncio

# /wiki
async def main(self, request):

	site = request.match_info.get('site', None)
	user_info = await self.root.get_user_info(request)
	current_navbar = self.root.html_header(self.root.BASE, user_info = user_info)

	# no site define -> show main
	if site == None or site == "":
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

