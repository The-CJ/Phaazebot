from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import html
from aiohttp.web import Request, Response
from Utils.Classes.htmlformatter import HTMLFormatter
from Platforms.Web.utils import getNavbar

async def notFound(cls:"WebIndex", WebRequest:Request, msg:str="") -> Response:
	req_str:str = html.escape("Not Found: "+WebRequest.path)

	cls.Web.BASE.Logger.debug(f"(Web) 404: {WebRequest.path}", require="web:404")

	Site404:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/pageNotFound.html")
	Site404.replace(msg=msg, path=req_str)

	site:str = cls.HTMLRoot.replace(
		replace_empty = True,

		title = "Phaaze | Not Found",
		header = getNavbar(),
		main = Site404.content
	)

	return cls.response(
		body=site,
		status=404,
		content_type='text/html'
	)
