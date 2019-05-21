from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import html
from aiohttp.web import Request, Response
from .utils import HTMLFormatter

async def NotFound(self:"WebIndex", Request:Request, msg:str="") -> Response:
	req_str:str = html.escape("Not Found: "+Request.path)

	self.Web.BASE.Logger.debug(f"(Web) 404: {Request.path}", require="web:404")

	Site404:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/pageNotFound.html")
	Site404.replace(msg=msg, path=req_str)

	site:str = self.HTMLRoot.replace(
		replace_empty = True,
		
		title = "Phaaze | Not Found",
		main = Site404.content
	)

	return self.response(
		body=site,
		status=404,
		content_type='text/html'
	)
