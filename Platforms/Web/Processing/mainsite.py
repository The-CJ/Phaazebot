from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

from aiohttp.web import Request, Response
from Utils.Classes.htmlformatter import HTMLFormatter
from Platforms.Web.utils import getNavbar

async def mainSite(self:"WebIndex", WebRequest:Request) -> Response:

	MainSite:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/main.html")

	site:str = self.HTMLRoot.replace(
		replace_empty = True,

		title = "Phaaze",
		header = getNavbar(),
		main = MainSite
	)

	return self.response(
		body=site,
		status=200,
		content_type='text/html'
	)
