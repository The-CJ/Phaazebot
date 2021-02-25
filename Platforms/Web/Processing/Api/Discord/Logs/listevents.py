from typing import TYPE_CHECKING, Dict, Any
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

import json
from aiohttp.web import Response
from Platforms.Discord.logging import TRACK_OPTIONS
from Utils.Classes.extendedrequest import ExtendedRequest

async def apiDiscordLogsListEvents(cls:"PhaazebotWeb", _WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /api/discord/logs/list
	"""

	result:Dict[str, Any] = dict(
		result=TRACK_OPTIONS,
		status=200
	)

	return cls.response(
		text=json.dumps(result),
		content_type="application/json",
		status=200
	)
