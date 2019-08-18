from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from main import Phaazebot

import requests

ROOT_URL:str = "https://osu.ppy.sh/api/"

async def getOsuUser(cls:"Phaazebot", search:str, mode:str="0", is_id:bool=False) -> list:
	"""
		api handler for osu requests, returns a dict or list
		mode:
				0 = osu
				1 = taiko
				2 = ctb
				3 = mania
	"""
	if not search: return None

	req:dict = dict(
		k = cls.Access.OSU_API_TOKEN,
		m = mode,
		type = "id" if is_id else "string",
		u = search
	)

	try:
		res:list = requests.get(ROOT_URL+"get_user", req).json()
	except:
		return None

	return res
