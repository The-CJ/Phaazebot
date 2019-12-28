from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from main import Phaazebot

import requests
from aiohttp.web import Request

ROOT_URL = "https://api.twitch.tv/helix/"
