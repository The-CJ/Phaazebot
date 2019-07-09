from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
	from Platforms.Web.index import WebIndex

import json
from aiohttp.web import Response, Request
from Utils.Classes.webrequestcontent import WebRequestContent
from Utils.Classes.webuserinfo import WebUserInfo
from ..errors import apiNotAllowed

async def apiAdminEvaluate(cls:"WebIndex", WebRequest:Request) -> Response:
	"""
		Default url: /api/admin/evaluate
	"""
	UserInfo:WebUserInfo = await cls.getUserInfo(WebRequest)
	if not UserInfo.checkRoles(["superadmin"]): return await apiNotAllowed(cls, WebRequest, msg="Superadmin rights required")

	Data:WebRequestContent = WebRequestContent(WebRequest)
	await Data.load()

	command:str = Data.get("command", None)
	corotine:bool = Data.get("corotine")

	# this is for easyer access
	locals()["BASE"] = cls.Web.BASE

	try:
		res:Any = eval(command)
		if corotine: res = await res
	except Exception as Fail:
		res:Any = Fail

	result = str(res)

	return cls.response(
		body=json.dumps(dict(result=result, status="200")),
		status=200,
		content_type='application/json'
	)