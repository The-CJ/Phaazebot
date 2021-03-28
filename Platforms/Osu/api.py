from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
	from main import Phaazebot

import requests
from Utils.Classes.osuuser import OsuUser

ROOT_URL:str = "https://osu.ppy.sh/api/"

async def getOsuUser(cls:"Phaazebot", search:str, mode:str="0", is_id:bool=False) -> Optional[OsuUser]:
	"""
	searches and returns the first user that hit the criteria, or none if nothing is found

	Keywords:
	---------
	* `mode` str : (Default: "0") [0 = osu, 1 = taiko, 2 = ctb, 3=mania]
	* `id_id` bool (Default: False) [Threat search as user id or name]
	"""
	if not search: return None

	req:dict = dict(
		k=cls.Access.osu_api_token,
		m=mode,
		type="id" if is_id else "string",
		u=search
	)

	res:requests.Response = requests.get(ROOT_URL+"get_user", req)

	try:
		return OsuUser(res.json()[0], mode=mode)
	except:
		return None