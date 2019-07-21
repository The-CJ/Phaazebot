from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request

async def apiDiscordCommandsGet(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/commands/get
	"""



	return cls.response(
		text=json.dumps( dict(r="",status=200) ),
		content_type="application/json",
		status=200
	)
