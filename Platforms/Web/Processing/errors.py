from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import html
from aiohttp.web import Request, Response

async def NotFound(self:"WebIndex", Request:Request, msg:str="") -> Response:
	req_str:str = html.escape("Not Found: "+Request.path)
	return self.response(
		body=f"site + {req_str}",
		status=404,
		content_type='text/html'
	)
