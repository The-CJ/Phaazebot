from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request
from Utils.Classes.webuserinfo import WebUserInfo
from Utils.Classes.webrequestcontent import WebRequestContent

async def apiAccountCreatePhaaze(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/account/phaaze/create
	"""

	UserInfo:WebUserInfo = await cls.getUserInfo(WebRequest)

	if UserInfo.found:
		cls.Web.BASE.Logger.debug(f"Account create already exist - User ID: {UserInfo.user_id}", require="api:create")
		return cls.response(
			body=json.dumps( dict(error="aleady_logged_in", status=400, msg="no registion needed, already logged in") ),
			content_type="application/json",
			status=400
		)

	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	return cls.response(
		text=json.dumps( dict(debug=Data.content,status=200) ),
		content_type="application/json",
		status=400
	)
