# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
# 	from Platforms.Web.index import WebIndex

# import html
# from aiohttp.web import Request, Response
from Utils.Classes.htmlformatter import HTMLFormatter

def getNavbar(style:str="", user_info=None) -> HTMLFormatter:
	navbar:HTMLFormatter = HTMLFormatter("Platforms/Web/Content/Html/Navbar/default.html")
	return navbar
