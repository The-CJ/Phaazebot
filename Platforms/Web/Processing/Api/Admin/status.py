from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex
	from main import Phaazebot

import json
import time
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.webuserinfo import WebUserInfo
from ..errors import apiNotAllowed

async def apiAdminStatus(cls:"WebIndex", WebRequest:Request, Data:WebRequestContent={}) -> Response:
	"""
		Default url: /api/admin/status
	"""
	UserInfo:WebUserInfo = await cls.getUserInfo(WebRequest)
	if not UserInfo.checkRoles(["admin", "superadmin"]): return await apiNotAllowed(cls, WebRequest, msg="Admin rights required")

	BASE:"Phaazebot" = cls.Web.BASE

	status:dict = dict()

	status["version"] = BASE.version
	status["uptime"] = time.time() - BASE.start_time

	status["modules"] = dict()
	for module in vars(BASE.Active):
		status["modules"][module] = bool(getattr(BASE.Active, module, False))

	return cls.response(
		body=json.dumps(dict(result=status, status=200)),
		status=200,
		content_type='application/json'
	)
