#BASE.modules._Web_.Base.root.web.Base

from importlib import reload
import traceback

async def main(self, request):
	site = open('_WEB_/content/main.html', 'r').read()

	user = await self.root.get_user_info(request)
	current_navbar = self.root.format_html(self.root.BASE.modules._Web_.Utils.get_navbar(active=''))

	site = self.root.format_html(site, navbar=current_navbar, user=user)

	return self.root.response(
		body=site,
		status=200,
		content_type='text/html'
	)

async def get_favicon(self, request):
	return self.root.response(
		body=open('_WEB_/content/favicon.ico', 'rb').read(),
		status=200,
		content_type='image/x-icon'
	)
