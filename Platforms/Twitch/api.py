from typing import TYPE_CHECKING, List, Any
if TYPE_CHECKING:
	from main import Phaazebot

import asyncio
import requests
from Platforms.Twitch.utils import emergencyTwitchClientCredentialTokenRefresh
from Utils.stringutils import randomString
from Utils.Classes.twitchstream import TwitchStream
from Utils.Classes.twitchgame import TwitchGame
from Utils.Classes.twitchuser import TwitchUser

ROOT_URL:str = "https://api.twitch.tv/helix/"
AUTH_URL:str = "https://id.twitch.tv/"
TWITCH_REQUEST_LIMIT:int = 100
TWITCH_REQUEST_WAIT:int = 2

def generateTwitchAuthLink(cls:"Phaazebot") -> str:
	"""
	used to create a link, that leads the user to twitch, where he authorizes our request.
	and is then send back to us, where he should have a ?code=123123 in his query
	"""

	auth_url:str = f"{AUTH_URL}oauth2/authorize"
	auth_params:dict = {
		"client_id": cls.Access.twitch_client_id,
		"redirect_uri": cls.Vars.twitch_redirect_link,
		"response_type": "code",
		"force_verify": True,
		"state": randomString(32),
		"scope": "user:read:email channel:read:subscriptions channel:read:redemptions bits:read"
	}

	Target:requests.Request = requests.Request(url=auth_url, params=auth_params)
	Prep:requests.PreparedRequest = Target.prepare()
	return Prep.url

async def twitchAPICall(cls:"Phaazebot", url:str, **kwargs:dict) -> requests.Response:
	"""
	all calles to twitch should been made via this.
	the function applies header and other stuff for authorisation
	so twitch knows its us.

	Optional keywords:
	------------------
	method `str` : (Default: 'GET')
	client_id `str` : (Default: Access.twitch_client_id)
	client_secret `str`
	auth_type `str` (Default: 'Bearer') ['Bearer' or 'OAuth']
	access_token `str` (Default: Access.twitch_client_credential_token)
	emergency_refesh_token `bool` (Default: True)
	"""
	method:str = kwargs.get("method", "GET")
	client_id:str = kwargs.get("client_id", cls.Access.twitch_client_id)
	client_secret:str = kwargs.get("client_secret", "")
	auth_type:str = kwargs.get("auth_type", "Bearer")
	access_token:str = kwargs.get("access_token", cls.Access.twitch_client_credential_token)
	emergency_refesh_token:bool = kwargs.get("emergency_refesh_token", True)

	headers:dict = dict()
	if client_id:
		# twitch usage of clientID and Client-ID is strange... i just give all
		headers["clientID"] = client_id
		headers["client_id"] = client_id
		headers["Client-ID"] = client_id
	if client_secret:
		headers["clientSecret"] = client_secret
		headers["client_secret"] = client_secret
		headers["Client-Secret"] = client_secret
	if auth_type:
		headers["Authorization"] = f"{auth_type} {access_token}"

	Resp:requests.Response = requests.request(method, url, headers=headers)
	if (Resp.status_code == 401) and (access_token == cls.Access.twitch_client_credential_token):
		# this will happen if our twitch credentials are outdated, for normal that should not happen, but if it does
		# we will start the Refresh protocol
		cls.Logger.warning("Twitch API call responsed with invalid auth")
		if emergency_refesh_token:
			emergencyTwitchClientCredentialTokenRefresh(cls)
			# after we did this the token should be refreshed, sooooo we just retry once and throw it back
			kwargs["emergency_refesh_token"] = False
			return await twitchAPICall(cls, url, **kwargs)
		else:
			cls.Logger.critical("Token retry runned once, but retry still failed")

	return Resp

async def getTwitchStreams(cls:"Phaazebot", item:str or list, item_type:str="user_id", limit:int=-1) -> List[TwitchStream]:
	"""
	get all currently live streams based on 'item' and 'item_type'
	Returns a list of TwitchStream()

	item [required]
	item_type : what are the contains of `item` (user_id, user_login, game_id, language)
	limit : max result number
	"""

	if type(item) is not list: item = [item]

	if limit > 0:
		item = item[:limit]

	total_results:List[TwitchStream] = []

	while item:

		part_request = item[:TWITCH_REQUEST_LIMIT]
		item = item[TWITCH_REQUEST_LIMIT:]

		part_result:List[TwitchStream] = await partGetTwitchStreams(cls, part_request, item_type)
		total_results.extend(part_result)

		if item: await asyncio.sleep(TWITCH_REQUEST_WAIT)

	return total_results

async def getTwitchGames(cls:"Phaazebot", item:str or list, item_type:str="id", limit:int=-1) -> List[TwitchGame]:
	"""
	get all game data based on 'item' and 'item_type'
	Returns a list of TwitchGame()

	item [required]
	item_type : what are the contains of `item` (id, name) | name must be exact, not good for search
	limit : max result number
	"""

	if type(item) is not list: item = [item]

	if limit > 0:
		item = item[:limit]

	total_results:List[TwitchGame] = []

	while item:

		part_request = item[:TWITCH_REQUEST_LIMIT]
		item = item[TWITCH_REQUEST_LIMIT:]

		part_result:List[TwitchGame] = await partGetTwitchGames(cls, part_request, item_type)
		total_results.extend(part_result)

		if item: await asyncio.sleep(TWITCH_REQUEST_WAIT)

	return total_results

async def getTwitchUsers(cls:"Phaazebot", item:str or list, item_type:str="id", limit:int=-1) -> List[TwitchUser]:
	"""
	get all game data based on 'item' and 'item_type'
	Returns a list of TwitchUser()

	item [required]
	item_type : what are the contains of `item` (id, login)
	limit : max result number
	"""

	if type(item) is not list: item = [item]

	if limit > 0:
		item = item[:limit]

	total_results:List[TwitchUser] = []

	while item:

		part_request = item[:TWITCH_REQUEST_LIMIT]
		item = item[TWITCH_REQUEST_LIMIT:]

		part_result:List[TwitchUser] = await partGetTwitchUsers(cls, part_request, item_type)
		total_results.extend(part_result)

		if item: await asyncio.sleep(TWITCH_REQUEST_WAIT)

	return total_results

# part requests (because some request must been broken down into smaller one)

async def partGetTwitchStreams(cls:"Phaazebot", item:List[Any], item_type:str) -> List[TwitchStream]:

	query:str = f"?first={len(item)}"

	for i in item:
		query += f"&{item_type}={str(i)}"

	link:str = f"{ROOT_URL}streams{query}"

	resp:dict = (await twitchAPICall(cls, link)).json()
	return [ TwitchStream(s) for s in resp.get("data", []) ]

async def partGetTwitchGames(cls:"Phaazebot", item:List[Any], item_type:str) -> List[TwitchGame]:

	query:str = f"?{item_type}={item.pop(0)}" # because we must start with a ?

	for i in item:
		query += f"&{item_type}={i}"

	link:str = f"{ROOT_URL}games{query}"

	resp:dict = (await twitchAPICall(cls, link)).json()
	return [ TwitchGame(s) for s in resp.get("data", []) ]

async def partGetTwitchUsers(cls:"Phaazebot", item:List[Any], item_type:str) -> List[TwitchUser]:

	query:str = f"?{item_type}={item.pop(0)}"

	for i in item:
		query += f"&{item_type}={i}"

	link:str = f"{ROOT_URL}users{query}"

	resp:dict = (await twitchAPICall(cls, link)).json()
	return [ TwitchUser(s) for s in resp.get("data", []) ]
