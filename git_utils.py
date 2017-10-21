#BASE.moduls.git_utils

import asyncio, os, time, requests, json

async def post_gist(BASE, data=None):
	"""Used to post huge information cluster, by giving back a gist link"""
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

