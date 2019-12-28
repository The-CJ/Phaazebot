from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from main import Phaazebot

import requests
from Utils.Classes.twitchstream import TwitchStream

ROOT_URL = "https://api.twitch.tv/helix/"

async def twitchAPICall(cls:"Phaazebot", url:str) -> requests.Response:
	"""
		all calles to twitch should been made via this.
		the function applies header and stuff so twitch knows its us.
	"""
	header:dict = {"Client-ID": cls.Access.TWITCH_API_TOKEN}
	return requests.get(url, headers=header)

async def getTwitchStreams(cls:"Phaazebot", item:str or list, item_type:str="user_id", limit:int=100) -> list:
	"""
		get all currently live streams based on 'stream' and 'search'
		Returns a list of TwitchStream()

		item [required]
		item_type : what are the contains of `item` (user_id, user_login, game_id, language)
		limit : max result number
	"""

	if type(item) is not list: item = [item]

	if limit > 100: limit = 100

	query:str = f"?first={limit}"

	for i in item:
		query += f"&{item_type}={i}"

	link:str = f"{ROOT_URL}streams{query}"

	resp:dict = (await twitchAPICall(cls, link)).json()
	return [ TwitchStream(s) for s in resp.get("data", []) ]
