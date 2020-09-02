from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from Platforms.Discord.logging import TRACK_OPTIONS
from aiohttp.web import Response, Request

async def apiDiscordLogsList(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
	Default url: /api/discord/logs/list
	"""
	return cls.response(
		text=json.dumps( dict(
			result=TRACK_OPTIONS,
			status=200)
		),
		content_type="application/json",
		status=200
	)
