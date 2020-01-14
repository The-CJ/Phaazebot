from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from main import Phaazebot

import requests
from Utils.Classes.twitchstream import TwitchStream
from Utils.Classes.twitchgame import TwitchGame
from Utils.Classes.twitchuser import TwitchUser

ROOT_URL = "https://api.twitch.tv/helix/"

async def twitchAPICall(cls:"Phaazebot", url:str) -> requests.Response:
	"""
		all calles to twitch should been made via this.
		the function applies header and stuff so twitch knows its us.
	"""
	header:dict = {"Client-ID": cls.Access.TWITCH_API_TOKEN}
	return requests.get(url, headers=header)

async def getTwitchStreams(cls:"Phaazebot", item:str or list, item_type:str="user_id", limit:int=-1) -> list:
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

	if len(item) > 100:
		cls.Logger.critical("Requesting more then 100 Streams -> limiting to 100 : TODO: implement mass requests")
		item = item[:100]

	query:str = f"?first={len(item)}"

	for i in item:
		query += f"&{item_type}={i}"

	link:str = f"{ROOT_URL}streams{query}"

	resp:dict = (await twitchAPICall(cls, link)).json()
	return [ TwitchStream(s) for s in resp.get("data", []) ]

async def getTwitchGames(cls:"Phaazebot", item:str or list, item_type:str="id") -> list:
	"""
		get all game data based on 'item' and 'item_type'
		Returns a list of TwitchGame()

		item [required]
		item_type : what are the contains of `item` (id, name) | name must be exact, not good for search
	"""

	if type(item) is not list: item = [item]

	if len(item) > 100:
		cls.Logger.critical("Requesting more then 100 Games -> limiting to 100 : TODO: implement mass requests")
		item = item[:100]

	query:str = f"?{item_type}={item.pop(0)}"

	for i in item:
		query += f"&{item_type}={i}"

	link:str = f"{ROOT_URL}games{query}"

	resp:dict = (await twitchAPICall(cls, link)).json()
	return [ TwitchGame(s) for s in resp.get("data", []) ]

async def getTwitchUsers(cls:"Phaazebot", item:str or list, item_type:str="id") -> list:
	"""
		get all game data based on 'item' and 'item_type'
		Returns a list of TwitchUser()

		item [required]
		item_type : what are the contains of `item` (id, login)
	"""

	if type(item) is not list: item = [item]

	if len(item) > 100:
		cls.Logger.critical("Requesting more then 100 User -> limiting to 100 : TODO: implement mass requests")
		item = item[:100]

	query:str = f"?{item_type}={item.pop(0)}"

	for i in item:
		query += f"&{item_type}={i}"

	link:str = f"{ROOT_URL}users{query}"

	resp:dict = (await twitchAPICall(cls, link)).json()
	return [ TwitchUser(s) for s in resp.get("data", []) ]
