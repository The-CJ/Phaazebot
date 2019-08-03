from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request

async def apiDiscordCommandsList(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/discord/commands/list
	"""

	# TODO: list all simple commands

	return cls.response(
		text=json.dumps( dict(result="", status=200) ),
		content_type="application/json",
		status=200
	)
