#BASE.modules._Web_.Base.root.web.Base

import asyncio

async def main(self, request):
	site = self.root.html_root

	current_navbar = self.root.html_header(self.root.BASE)
	main_site = open('_WEB_/content/main.html','r').read()

	site = self.root.format_html(site,
		title="Phaaze",
		header=current_navbar,
		main=main_site
	)

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

async def cert(self, request):
	cert_root = '/etc/ssl/certs/phaaze/'
	cert_path = '.well-known/acme-challenge/'
	cert_file = request.match_info.get('cert_file', None)

	if cert_file == None:
		return await self.root.web.page_not_found(request)

	cert_file = cert_file.replace('..','')
	try:
		file_ = open(cert_root+cert_path+cert_file, 'rb').read()
		self.root.BASE.modules.Console.WARNING('CERT-Info - Successfull call to certfile: '+cert_file)
	except:
		self.root.BASE.modules.Console.ERROR(f"CERT-Info - Invalid call to certs: '{str(cert_file)}' from IP: {request.remote}")
		return await self.root.web.page_not_found(request)

	return self.root.response(
		body=file_,
		status=200,
		content_type='text/plain'
	)
