#BASE.modules._Web_.Base.root.Base

from importlib import reload
import traceback

def main_(BASE, info, root):
	session=info.get('cookies', {}).get('phaaze_session', None)
	phaaze_username = info.get('values', {}).get('phaaze_username', None)
	password = info.get('values', {}).get('password', None)
	api_token = info.get('values', {}).get('api_token', None)

	info['user'] = BASE.api.utils.get_phaaze_user(BASE, phaaze_username=phaaze_username, password=password, session=session, api_token=api_token )
	info['root'] = root

	#main site
	if len(info['path']) == 0:
		return main_site(BASE, info)

	#api stuff
	elif info['path'][0].lower() == 'api':
		return BASE.api.call(BASE, info)

	#icon
	elif info['path'][0].lower() == 'favicon.ico':
		return get_favicon()

	#something with js
	elif info['path'][0].lower() == 'js':
		info['path'].pop(0)
		return root.js.main(BASE, info, root)

	#something with css
	elif info['path'][0].lower() == 'css':
		info['path'].pop(0)
		return root.css.main(BASE, info, root)

	#some image
	elif info['path'][0].lower() == 'img':
		info['path'].pop(0)
		return root.img.main(BASE, info, root)

	#admin Page
	elif info['path'][0].lower() == 'admin':
		info['path'].pop(0)
		return root.admin.admin.main(BASE, info, root)

	#discord
	elif info['path'][0].lower() == 'discord':
		info['path'].pop(0)
		return root.discord.main.main(BASE, info, root)

	#fileserver
	elif info['path'][0].lower() == 'fileserver':
		info['path'].pop(0)
		return root.fileserver.main.main(BASE, info, root)

	#wiki
	elif info['path'][0].lower() == 'wiki':
		info['path'].pop(0)
		return root.wiki.main.main(BASE, info, root)

	#account
	elif info['path'][0].lower() == 'account':
		info['path'].pop(0)
		return root.account.account.main(BASE, info)

	#leads to another site
	else:
		print("Tryed access: "+info['path'][0])
		return root.page_not_found.page_not_found(BASE, info, root)

def main(self, request):
	site = open('_WEB_/content/main.html', 'r').read()

	current_navbar = self.format_html(self.BASE.modules._Web_.Utils.get_navbar(active=''))

	site = self.format_html(site, navbar=current_navbar)

	return self.response(
		body=site,
		status=200,
		content_type='text/html'
	)

def get_favicon(self, request):
	return self.response(
		body=open('_WEB_/content/favicon.ico', 'rb').read(),
		status=200,
		content_type='image/x-icon'
	)
