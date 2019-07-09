from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from ..errors import apiMissingValidMethod

async def apiAdminModule(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/admin/module
	"""
	module:str = WebRequest.match_info.get("module", None)
	if not module: return await apiMissingValidMethod(cls, WebRequest)

	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	return await apiMissingValidMethod(cls, WebRequest, msg=f"'{module}' is not a known module")
