from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

import html
from aiohttp.web import Response
from Utils.Classes.htmlformatter import HTMLFormatter
from Utils.Classes.extendedrequest import ExtendedRequest
from Platforms.Web.utils import getNavbar

async def notFound(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, msg:str="") -> Response:
	req_str:str = html.escape("Not Found: "+WebRequest.path)

	cls.BASE.Logger.debug(f"(Web) 404: {WebRequest.path}", require="web:404")

	Site404:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/pageNotFound.html")
	Site404.replace(msg=msg, path=req_str)

	site:str = cls.HTMLRoot.replace(
		replace_empty=True,

		title="Phaaze | Not Found",
		header=getNavbar(),
		main=Site404.content
	)

	return cls.response(
		body=site,
		status=404,
		content_type='text/html'
	)

async def notAllowed(cls:"PhaazebotWeb", WebRequest:ExtendedRequest, msg:str="") -> Response:
	req_str:str = html.escape("Not Allowed: "+WebRequest.path)

	cls.BASE.Logger.debug(f"(Web) 401: {WebRequest.path}", require="web:401")

	Site401:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/actionNotAllowed.html")
	Site401.replace(msg=msg, path=req_str)

	site:str = cls.HTMLRoot.replace(
		replace_empty=True,

		title="Phaaze | Not Allowed",
		header=getNavbar(),
		main=Site401.content
	)

	return cls.response(
		body=site,
		status=401,
		content_type='text/html'
	)

async def underDev(cls:"PhaazebotWeb", WebRequest:ExtendedRequest) -> Response:
	cls.BASE.Logger.debug(f"(Web) 400: {WebRequest.path}", require="web:underDev")

	SiteDev:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/underDev.html")
	site:str = cls.HTMLRoot.replace(
		replace_empty=True,

		title="Phaaze | Under development",
		header=getNavbar(),
		main=SiteDev.content
	)

	return cls.response(
		body=site,
		status=400,
		content_type='text/html'
	)
