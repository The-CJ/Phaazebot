#BASE.moduls.git_utils

import asyncio, os, time, requests, json

async def post_gist(BASE=None, data=None):
	data = dict()
	data['description'] = 'Example Gist for Phaaze Level logs'
	data['public'] = True
	data['files'] = dict()
	data['files']['example.txt'] = dict(content = 'SOMTHING DUMP')

	data = json.dumps(data)
	print(data)

	resp = requests.post('https://api.github.com/gists', data = data)
	try:
		print(resp.text)
	except:
		pass
	try:
		print(resp.text())
	except:
		pass

