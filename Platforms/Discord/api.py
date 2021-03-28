from typing import TYPE_CHECKING, Optional, List
if TYPE_CHECKING:
	from phaazebot import Phaazebot

import requests
from aiohttp.web import Request

ROOT_URL = "https://discordapp.com/api/v6/"

def generateDiscordAuthLink(cls:"Phaazebot") -> str:
	"""
	used to create a link, that leads the user to discord, where he authorizes our request.
	and is then send back to us, where he should have a ?code=123123 in his query
	"""

	auth_url:str = f"{ROOT_URL}oauth2/authorize"
	auth_params:dict = {
		"client_id": cls.Vars.discord_bot_id,
		"redirect_uri": cls.Vars.discord_redirect_link,
		"response_type": "code",
		"scope": "identify email connections guilds"
	}

	Target:requests.Request = requests.Request(url=auth_url, params=auth_params)
	Prep:requests.PreparedRequest = Target.prepare()
	return Prep.url

async def translateDiscordToken(cls:"Phaazebot", WebRequest:Request) -> Optional[dict]:
	"""
	Used to complete a oauth verification via a token the user provides in his GET query
	(It has to be there)
	We then get all info's we want/need from discord
	"""
	code:str = WebRequest.query.get("code", "")
	if not code:
		cls.Logger.debug("translateDiscordToken called without code", require="discord:api")
		return None

	req:dict = dict(
		client_id=cls.Vars.discord_bot_id,
		client_secret=cls.Access.discord_secret,
		grant_type="authorization_code",
		code=code,
		redirect_uri=cls.Vars.discord_redirect_link
	)
	headers:dict = {'Content-Type': 'application/x-www-form-urlencoded'}

	res = requests.post(ROOT_URL+"oauth2/token", req, headers)
	return res.json()

async def getDiscordUser(_cls:"Phaazebot", access_token:str) -> dict:
	"""
	get all info's discord allows us to see for a user
	"""
	headers:dict = {"Authorization": f"Bearer {access_token}"}

	res:requests.Response = requests.get(ROOT_URL+"users/@me", headers=headers)

	return res.json()

async def getDiscordUserServers(_cls:"Phaazebot", access_token:str) -> List[dict]:
	"""
	get all base info' s of guilds/servers a user is on
	(requires the access_token to have the right scope so we are allowed to see it)
	"""
	headers:dict = {"Authorization": f"Bearer {access_token}"}

	res:requests.Response = requests.get(ROOT_URL+"users/@me/guilds", headers=headers)

	return res.json()
