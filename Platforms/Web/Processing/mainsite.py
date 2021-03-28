from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.main_web import PhaazebotWeb

from aiohttp.web import Response
from Utils.Classes.htmlformatter import HTMLFormatter
from Utils.Classes.extendedrequest import ExtendedRequest
from Platforms.Web.index import PhaazeWebIndex
from Platforms.Web.utils import getNavbar

@PhaazeWebIndex.get('/')
async def mainSite(cls:"PhaazebotWeb", _WebRequest:ExtendedRequest) -> Response:
	"""
	Default url: /
	"""
	MainSite:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/main.html")

	site:str = cls.HTMLRoot.replace(
		replace_empty=True,

		title="Phaaze",
		header=getNavbar(),
		main=MainSite
	)

	return cls.response(
		body=site,
		status=200,
		content_type='text/html'
	)
