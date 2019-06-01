from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

from aiohttp.web import Response, Request
from Utils.Classes.webuserinfo import WebUserInfo
from Platforms.Web.utils import getNavbar

async def accountCreate(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /account/create
	"""
	UserInfo:WebUserInfo = await cls.getUserInfo(WebRequest)

	if UserInfo.found: return await cls.accountMain(WebRequest)

	site:str = cls.HTMLRoot.replace(
		replace_empty = True,

		title = "Phaaze | Account create",
		header = getNavbar()
	)

	return cls.response(
		body=site,
		status=200,
		content_type='text/html'
	)
