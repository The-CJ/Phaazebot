import json, requests

VERSION = "v6"
ROOT = "https://discordapp.com/api/{}/".format(VERSION)

def get_user(oauth_key):
	try:
		t = requests.get(ROOT+"users/@me", headers={'Authorization': 'Bearer {}'.format(oauth_key)})
		return t.json()
	except Exception as e:
		raise e

