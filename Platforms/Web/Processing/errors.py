from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import html
from aiohttp.web import Request, Response
from .utils import HTMLFormatter

async def NotFound(self:"WebIndex", Request:Request, msg:str="") -> Response:
	req_str:str = html.escape("Not Found: "+Request.path)

	self.Web.BASE.Logger.debug(f"(Web) 404: {Request.path}", require="web:404")

	site:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/pageNotFound.html")
	site.replace(mag=msg, path=req_str)

	return self.response(
		body=site.content,
		status=404,
		content_type='text/html'
	)
