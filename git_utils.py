#BASE.moduls.git_utils

import asyncio, os, time, requests, json

async def post_gist(BASE, data=None, description=None, name=None, content=None):
	"""Used to post huge information cluster, by giving back a gist link"""
	if data == None:
		data = dict(
			description = description,
			public = True,
			files = dict()
		)
		data['files'][name] = dict(content=content)

	try:
		data = json.dumps(data)
		resp = requests.post('https://api.github.com/gists', data = data)
	except:
		return None

	try:
		response = resp.json()
		return response['html_url']

	except:
		return None
