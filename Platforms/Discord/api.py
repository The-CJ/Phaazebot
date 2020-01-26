from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from main import Phaazebot

import requests
from aiohttp.web import Request

ROOT_URL = "https://discordapp.com/api/v6/"

async def translateDiscordToken(cls:"Phaazebot", WebRequest:Request) -> dict or None:
	"""
		Used to complete a oauth verification via a token the user provies in his GET query
		(It has to be there)
		We then get all infos we want/need from discord
	"""
	code:str = WebRequest.query.get("code", None)
	if not code:
		cls.Logger.debug("translateDiscordToken called without code", require="discord:api")
		return None

	req:dict = dict(
		client_id = cls.Vars.DISCORD_BOT_ID,
		client_secret = cls.Access.DISCORD_SECRET,
		grant_type = "authorization_code",
		code = code,
		redirect_uri = cls.Vars.DISCORD_REDIRECT_LINK
	)
	headers:dict = {'Content-Type': 'application/x-www-form-urlencoded'}

	res = requests.post(ROOT_URL+"oauth2/token", req, headers)
	return res.json()

async def getDiscordUser(cls:"Phaazebot", access_token:str) -> dict:
	"""
		get all infos discord allowes us to see for a user
	"""
	headers:dict = {"Authorization": f"Bearer {access_token}"}

	res:requests.Response = requests.get(ROOT_URL+"users/@me", headers=headers)

	return res.json()

async def getDiscordUserServers(cls:"Phaazebot", access_token:str) -> list:
	"""
		get all base infos of guilds/servers a user is on
		(requires the access_token to have the right scope so we are allowed to see it)
	"""
	headers:dict = {"Authorization": f"Bearer {access_token}"}

	res:requests.Response = requests.get(ROOT_URL+"users/@me/guilds", headers=headers)

	return res.json()
