from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.webuserinfo import WebUserInfo
from ..errors import apiMissingValidMethod, apiNotAllowed

async def apiAdminModule(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/admin/module
	"""

	UserInfo:WebUserInfo = await cls.getUserInfo(WebRequest)
	if not UserInfo.checkRoles(["admin", "superadmin"]): return await apiNotAllowed(cls, WebRequest, msg="Admin rights required")

	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	module:str = str(Data.get("module"))
	state:bool = bool(Data.get("state"))

	if not hasattr(cls.Web.BASE.Active, module):
		return await apiMissingValidMethod(cls, WebRequest, msg=f"module '{module}' not avariable")

	setattr(cls.Web.BASE.Active, module, state)
	cls.Web.BASE.Logger.warning(f"Module change state: '{module}' now '{state}'")

	return cls.response(
		body=json.dumps(dict(msg=f"state for module: '{module}' is now: {str(state)}", status=200)),
		status=200,
		content_type='application/json'
	)
